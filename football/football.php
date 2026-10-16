<?php
declare(strict_types=1);
// Per-installation pagination. State stays outside the public document root.
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store, private, max-age=0');
function respond(array $data, int $status = 200): never {
    http_response_code($status);
    echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR);
    exit;
}
if (!in_array($_SERVER['REQUEST_METHOD'] ?? 'GET', ['GET', 'HEAD'], true)) {
    header('Allow: GET, HEAD'); respond(['error'=>'Method not allowed'], 405);
}
$device = $_GET['device'] ?? '';
if (!is_string($device) || !preg_match('/^[A-Za-z0-9_-]{1,128}$/D', $device)) {
    respond(['error'=>'Provide a unique device ID: ?device=your-device-name'], 400);
}
$rows = filter_var($_GET['rows'] ?? 14, FILTER_VALIDATE_INT);
if ($rows === false || $rows < 3 || $rows > 14) respond(['error'=>'rows must be between 3 and 14'], 400);
try {
    $feed = json_decode(file_get_contents(__DIR__.'/football.json'), true, 512, JSON_THROW_ON_ERROR);
    $pages = []; $lines = []; $last = null; $count = 0;
    foreach ($feed['matches'] ?? [] as $match) {
        $group = $match['date'].'  '.$match['competition'];
        $needed = $group !== $last ? 2 : 1;
        if ($lines && (count($lines) + $needed > $rows || $count >= 12)) {
            $pages[] = $lines; $lines = []; $last = null; $count = 0;
        }
        if ($group !== $last) {
            $lines[] = ['kind'=>'heading', 'text'=>$group]; $last = $group;
        }
        $lines[] = ['kind'=>'match'] + $match; $count++;
    }
    if ($lines) $pages[] = $lines;
    if (!$pages) $pages = [[]];
    // Score corrections also restart the cycle; upstream check timestamps do not.
    $version = hash('sha256', json_encode([$rows, $feed['matches'] ?? []]));
    $key = hash('sha256', $device.':'.$rows);
    $db = new PDO('sqlite:/var/lib/trmnl-football/devices.sqlite');
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $db->exec('PRAGMA busy_timeout=5000');
    $db->exec('CREATE TABLE IF NOT EXISTS devices (id TEXT PRIMARY KEY, version TEXT NOT NULL, page INTEGER NOT NULL, served INTEGER NOT NULL)');
    $db->exec('BEGIN IMMEDIATE');
    $stmt = $db->prepare('SELECT version,page,served FROM devices WHERE id=?');
    $stmt->execute([$key]); $state = $stmt->fetch(PDO::FETCH_ASSOC);
    $now = time(); $page = 0;
    if ($state && $state['version'] === $version) {
        // Near-immediate retries receive the same page rather than skipping results.
        $page = $now - (int)$state['served'] < 30 ? (int)$state['page'] : ((int)$state['page'] + 1) % count($pages);
    }
    if (($_SERVER['REQUEST_METHOD'] ?? 'GET') !== 'HEAD') {
        $served = $state && $state['version'] === $version && $now - (int)$state['served'] < 30 ? (int)$state['served'] : $now;
        $stmt = $db->prepare('INSERT OR REPLACE INTO devices VALUES (?,?,?,?)');
        $stmt->execute([$key, $version, $page, $served]);
        $db->exec('DELETE FROM devices WHERE served < '.($now - 90*86400));
    }
    $db->exec('COMMIT');
    $feed['lines'] = $pages[$page];
    $feed['count'] = count(array_filter($feed['lines'], fn($row)=>$row['kind']==='match'));
    $feed['page_number'] = $page + 1;
    $feed['page_count'] = count($pages);
    $feed['page_label'] = ($page + 1).'/'.count($pages);
    unset($feed['matches']);
    if (($_SERVER['REQUEST_METHOD'] ?? 'GET') === 'HEAD') exit;
    respond($feed);
} catch (Throwable $e) {
    error_log('TRMNL football pagination: '.$e->getMessage());
    respond(['error'=>'Results temporarily unavailable; please retry'], 503);
}

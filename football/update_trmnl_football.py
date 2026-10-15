#!/usr/bin/env python3
"""Public men's football results for Pete's TRMNL. No credentials required."""
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import re
import urllib.request
from zoneinfo import ZoneInfo

ROOT = Path('/var/www/salsbury.uk')
OUT = ROOT / 'trmnl'
CACHE = ROOT / '.trmnl-football-cache'
TZ = ZoneInfo('Europe/London')
COMPETITIONS = {
 'Championship':'CHAMPIONSHIP', 'English Championship':'CHAMPIONSHIP',
 'Premier League':'PREMIER LEAGUE', 'English Premier League':'PREMIER LEAGUE',
 'FA Cup':'FA CUP', 'English FA Cup':'FA CUP',
 'English League Cup':'LEAGUE CUP', 'EFL Cup':'LEAGUE CUP', 'League Cup':'LEAGUE CUP',
 'Community Shield':'COMMUNITY SHIELD', 'FA Community Shield':'COMMUNITY SHIELD',
 'English Community Shield':'COMMUNITY SHIELD',
 'UEFA Champions League':'CHAMPIONS LEAGUE',
 'UEFA Europa League':'EUROPA LEAGUE',
 'UEFA Conference League':'CONFERENCE LEAGUE',
 'UEFA Europa Conference League':'CONFERENCE LEAGUE',
 'UEFA Super Cup':'UEFA SUPER CUP',
 'FIFA World Cup':'WORLD CUP', 'World Cup':'WORLD CUP',
 'FIFA Club World Cup':'CLUB WORLD CUP', 'Club World Cup':'CLUB WORLD CUP',
 'UEFA European Championship':'EUROS', 'European Championship':'EUROS',
 'UEFA Euro':'EUROS', 'UEFA Nations League':'NATIONS LEAGUE',
 'World Cup Qualifying - European':'WORLD CUP QUALIFYING',
 'World Cup Qualifying - South American':'WORLD CUP QUALIFYING',
 'World Cup Qualifying - African':'WORLD CUP QUALIFYING',
 'World Cup Qualifying - Asian':'WORLD CUP QUALIFYING',
 'World Cup Qualifying - North/Central American':'WORLD CUP QUALIFYING',
 'World Cup Qualifying - Oceania':'WORLD CUP QUALIFYING',
 'European Championship Qualifying':'EURO QUALIFYING',
}
def groups(obj):
 if isinstance(obj,dict):
  if 'eventGroups' in obj:
   yield from obj['eventGroups']
  else:
   for v in obj.values(): yield from groups(v)
 elif isinstance(obj,list):
  for v in obj: yield from groups(v)

def events(obj):
 if isinstance(obj,dict):
  if 'home' in obj and 'away' in obj and 'startDateTime' in obj:
   yield obj
  else:
   for v in obj.values(): yield from events(v)
 elif isinstance(obj,list):
  for v in obj: yield from events(v)

def parse(html, now):
 match=re.search(r'window\.__INITIAL_DATA__=(.*?);</script>',html,re.S)
 if not match: raise ValueError('BBC results structure missing')
 payload=json.loads(json.loads(match.group(1)))
 result=[]
 for group in groups(payload):
  label=group.get('displayLabel','')
  comp=COMPETITIONS.get(label)
  if not comp: continue
  for event in events(group):
   # Exact competition allowlist also excludes women's and youth competitions.
   tournament=event.get('tournament',{}).get('disambiguatedName',label)
   if re.search(r'women|under[\s-]?\d|u[\s-]?(17|19|20|21|23)\b',tournament,re.I):continue
   status=event.get('periodLabel',{}).get('value','')
   if event.get('status')!='PostEvent' or status not in ('FT','AET','Pens','PEN','PENS'): continue
   kickoff=dt.datetime.fromisoformat(event['startDateTime'].replace('Z','+00:00'))
   if kickoff>now:continue
   home,away=event['home'],event['away']
   hs,aws=home.get('score'),away.get('score')
   if hs is None or aws is None or not str(hs).isdigit() or not str(aws).isdigit(): continue
   local=kickoff.astimezone(TZ)
   note=''
   hr,ar=home.get('runningScores',{}),away.get('runningScores',{})
   hp=hr.get('penalties',hr.get('shootout'))
   ap=ar.get('penalties',ar.get('shootout'))
   if hp is not None and ap is not None:note=f'P {hp}-{ap}'
   elif status.upper() in ('PENS','PEN'):note='PENS'
   elif status=='AET':note='AET'
   # Retain the provider's explanatory shootout/aggregate text for inspection.
   detail=event.get('statusComment',{}).get('value','')
   result.append(dict(id=event.get('id'),competition=comp,date=local.strftime('%d %b').upper(),
    date_iso=local.date().isoformat(),kickoff=event['startDateTime'],
    home=home.get('fullName') or home.get('shortName'),
    away=away.get('fullName') or away.get('shortName'),
    home_score=str(hs),away_score=str(aws),note=note,detail=detail,status=status))
 return result

def fetch_day(day,today,now,errors):
 path=CACHE/(day.isoformat()+'.json')
 ttl=600 if (today-day).days<2 else 86400
 if path.exists() and now.timestamp()-path.stat().st_mtime<ttl:
  return json.loads(path.read_text())
 try:
  req=urllib.request.Request('https://www.bbc.co.uk/sport/football/scores-fixtures/'+day.isoformat(),
    headers={'User-Agent':'PetesTRMNLFootball/1.0'})
  with urllib.request.urlopen(req,timeout=12) as response:
   data=parse(response.read().decode(),now)
  atomic(path,data)
  return data
 except Exception as exc:
  errors.append(day.isoformat()+': '+str(exc))
  return json.loads(path.read_text()) if path.exists() else []

def atomic(path,data):
 tmp=path.with_suffix('.tmp')
 tmp.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
 os.replace(tmp,path)

def build(matches,now,errors):
 matches=sorted({m['id']:m for m in matches}.values(),key=lambda m:(m['kickoff'],m['competition'],m['home']),reverse=True)
 # 14 text lines, including date/competition headings; at most 12 results.
 lines=[];last=None;shown=0
 for m in matches:
  key=(m['date'],m['competition'])
  needed=2 if key!=last else 1
  if len(lines)+needed>14 or shown>=12:break
  if key!=last:
   lines.append({'kind':'heading','text':m['date']+'  '+m['competition']});last=key
  lines.append({'kind':'match',**m});shown+=1
 return {'title':'FOOTBALL RESULTS','page':'302','updated':now.astimezone(TZ).strftime('%d %b %H:%M'),
  'checked_at':now.isoformat(),'source':'BBC Sport','warning':'Some dates could not be checked' if errors else '',
  'count':shown,'lines':lines,'matches':matches[:60],
  'message':'' if lines else 'No completed matches found in the last 30 days.'}

def main():
 OUT.mkdir(exist_ok=True);CACHE.mkdir(exist_ok=True)
 with (CACHE/'update.lock').open('w') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:return
  now=dt.datetime.now(dt.timezone.utc);today=now.astimezone(TZ).date()
  matches=[];errors=[]
  for offset in range(30):
   matches.extend(fetch_day(today-dt.timedelta(days=offset),today,now,errors))
   if len(matches)>=24 and offset>=1:break
  data=build(matches,now,errors)
  if not data['lines'] and errors and (OUT/'football.json').exists():
   old=json.loads((OUT/'football.json').read_text())
   old['warning']='Feed unavailable - showing saved results'
   atomic(OUT/'football.json',old)
  else:atomic(OUT/'football.json',data)
  for p in CACHE.glob('*.json'):
   if now.timestamp()-p.stat().st_mtime>35*86400:p.unlink()
  print(json.dumps({'results':data['count'],'dates_checked':offset+1,'errors':errors,'updated':data['updated']}))
if __name__=='__main__':main()

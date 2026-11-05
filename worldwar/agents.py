import json, os, requests
from .data import ACTIONS
SYSTEM_PROMPT="""You are the head of government in a fictionalized geopolitical strategy simulation. Control only your own country. Choose one legal game action per turn. Military conflict is abstracted into non-operational game statistics: do not provide real-world attack plans, targeting, weapons instructions or tactical details. Consider economy, public stability, technology, diplomacy, resources and national interests. Return ONLY JSON with keys action, target, rationale. action must be one of: """+", ".join(ACTIONS)+". target must be another country name for diplomacy, trade, sanction or conflict; otherwise null. rationale must be one concise sentence."
def _json(raw):
 raw=raw.strip()
 if raw.startswith('```'): raw=raw.split('\n',1)[-1].rsplit('```',1)[0].strip()
 a,b=raw.find('{'),raw.rfind('}')
 if a<0 or b<=a: raise ValueError('No JSON object returned')
 return json.loads(raw[a:b+1])
def _fallback(country,state):
 c=state['countries'][country]
 if c['stability']<43: return {'action':'social_program','target':None,'rationale':'Stability is under pressure; prioritizing public support.'}
 if c['tech']<75 and state['turn']%3==0: return {'action':'research','target':None,'rationale':'Investing in long-term technological capacity.'}
 if c['gdp']<2: return {'action':'invest_economy','target':None,'rationale':'Strengthening domestic economic capacity.'}
 if state['turn']%5==0:
  other=max((n for n in state['countries'] if n!=country),key=lambda n:state['relations'][country][n])
  return {'action':'diplomacy','target':other,'rationale':'Building a more stable diplomatic environment.'}
 if c['military']<55: return {'action':'mobilize','target':None,'rationale':'Improving abstract defensive readiness.'}
 return {'action':'invest_economy','target':None,'rationale':'Maintaining steady economic development.'}
def choose_action(country,state,provider='Fallback',model=None):
 if provider=='Fallback': return _fallback(country,state),'Fallback'
 c=state['countries'][country]
 prompt={'country':country,'profile':c,'turn':state['turn'],'relations':state['relations'][country],'recent_events':state['events'][-8:]}
 try:
  if provider=='Ollama':
   base=os.getenv('OLLAMA_BASE_URL','http://localhost:11434').rstrip('/'); chosen=model or os.getenv('OLLAMA_MODEL','qwen2.5:3b')
   r=requests.post(base+'/api/chat',json={'model':chosen,'stream':False,'format':'json','messages':[{'role':'system','content':SYSTEM_PROMPT},{'role':'user','content':json.dumps(prompt)}]},timeout=90); r.raise_for_status(); raw=r.json()['message']['content']
  else:
   base=os.getenv('CLOUD_BASE_URL','https://api.openai.com/v1').rstrip('/'); key=os.getenv('CLOUD_API_KEY',''); chosen=model or os.getenv('CLOUD_MODEL','gpt-4.1-mini')
   if not key: raise RuntimeError('CLOUD_API_KEY is missing')
   r=requests.post(base+'/chat/completions',headers={'Authorization':'Bearer '+key},json={'model':chosen,'temperature':0.7,'response_format':{'type':'json_object'},'messages':[{'role':'system','content':SYSTEM_PROMPT},{'role':'user','content':json.dumps(prompt)}]},timeout=90); r.raise_for_status(); raw=r.json()['choices'][0]['message']['content']
  d=_json(raw)
  if d.get('action') not in ACTIONS: raise ValueError('Unknown action')
  target=d.get('target'); target=target if target in state['countries'] and target!=country else None
  return {'action':d['action'],'target':target,'rationale':str(d.get('rationale',''))[:240]},provider
 except Exception as e:
  d=_fallback(country,state); d['rationale']=f'Fallback used ({type(e).__name__}); '+d['rationale']; return d,'Fallback'

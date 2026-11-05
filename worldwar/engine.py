import copy, random
from .data import COUNTRIES
from .agents import choose_action
def new_world(seed=7):
 random.seed(seed); countries=copy.deepcopy(COUNTRIES); names=list(countries)
 relations={a:{b:(0 if a==b else random.randint(-20,25)) for b in names} for a in names}
 return {'turn':0,'countries':countries,'relations':relations,'events':[{'turn':0,'kind':'world','text':'The simulation begins. Governments are taking office.'}],'history':[]}
def _event(s,k,t,r=''):
 s['events'].append({'turn':s['turn'],'kind':k,'text':t,'rationale':r}); s['events']=s['events'][-250:]
def clamp(v,lo=0,hi=100): return max(lo,min(hi,v))
def apply_action(s,country,action,target=None,rationale=''):
 cs,rel=s['countries'],s['relations']; c=cs[country]; valid=target in cs and target!=country
 if action=='invest_economy': c['gdp']=round(c['gdp']*1.012+0.015,3); c['stability']=clamp(c['stability']+.5); msg=f'{country} invested in economic development.'; kind='economy'
 elif action=='research': c['tech']=clamp(c['tech']+2); c['gdp']=round(c['gdp']*1.003,3); msg=f'{country} funded a research programme.'; kind='technology'
 elif action=='social_program': c['stability']=clamp(c['stability']+4); c['gdp']=round(max(.05,c['gdp']*.997),3); msg=f'{country} launched a public support programme.'; kind='politics'
 elif action=='diplomacy' and valid: rel[country][target]=clamp(rel[country][target]+12,-100,100); rel[target][country]=clamp(rel[target][country]+5,-100,100); msg=f'{country} opened diplomatic talks with {target}.'; kind='diplomacy'
 elif action=='trade' and valid: rel[country][target]=clamp(rel[country][target]+7,-100,100); rel[target][country]=clamp(rel[target][country]+7,-100,100); c['gdp']=round(c['gdp']*1.008,3); cs[target]['gdp']=round(cs[target]['gdp']*1.006,3); msg=f'{country} and {target} signed a simulated trade agreement.'; kind='economy'
 elif action=='mobilize': c['military']=clamp(c['military']+3); c['gdp']=round(max(.05,c['gdp']*.998),3); msg=f'{country} increased abstract readiness.'; kind='military'
 elif action=='deescalate' and valid: rel[country][target]=clamp(rel[country][target]+18,-100,100); rel[target][country]=clamp(rel[target][country]+12,-100,100); msg=f'{country} proposed de-escalation to {target}.'; kind='diplomacy'
 elif action=='sanction' and valid: rel[country][target]=clamp(rel[country][target]-12,-100,100); cs[target]['gdp']=round(max(.05,cs[target]['gdp']*.992),3); c['gdp']=round(max(.05,c['gdp']*.998),3); msg=f'{country} imposed simulated economic restrictions on {target}.'; kind='economy'
 elif action=='conflict' and valid:
  # Abstract contest only: no real-world tactics or operational detail.
  a=c['military']*.55+c['tech']*.25+c['stability']*.20+random.uniform(-8,8); b=cs[target]['military']*.55+cs[target]['tech']*.25+cs[target]['stability']*.20+random.uniform(-8,8)
  winner,loser=(country,target) if a>=b else (target,country); cs[winner]['military']=clamp(cs[winner]['military']-1.5); cs[loser]['military']=clamp(cs[loser]['military']-5); cs[loser]['stability']=clamp(cs[loser]['stability']-4); cs[loser]['gdp']=round(max(.05,cs[loser]['gdp']*.975),3); rel[country][target]=clamp(rel[country][target]-25,-100,100); rel[target][country]=clamp(rel[target][country]-25,-100,100); msg=f'Abstract strategic contest: {winner} gained the upper hand over {loser}.'; kind='conflict'
 else: c['gdp']=round(c['gdp']*1.005,3); msg=f'{country} maintained its current policy.'; kind='world'
 _event(s,kind,msg,rationale)
def _passive(s):
 for c in s['countries'].values():
  c['gdp']=round(max(.05,c['gdp']*(1+(c['tech']-50)/10000)),3); c['stability']=clamp(c['stability']+(.15 if c['gdp']>1 else -.05)-max(0,50-c['stability'])*.006); c['population']=round(c['population']*(1+.0008+(c['stability']-50)/100000),2); c['resources']=clamp(c['resources']-.08+(.12 if c['gdp']<1 else 0)); c['tech']=clamp(c['tech']+.08)
def advance_turn(state,providers=None):
 state['turn']+=1; snap=copy.deepcopy(state); decisions=[]; providers=providers or {}
 for name in snap['countries']:
  cfg=providers.get(name,{}); d,p=choose_action(name,snap,cfg.get('provider','Fallback'),cfg.get('model')); decisions.append((name,d,p))
 for name,d,p in decisions: apply_action(state,name,d['action'],d.get('target'),d.get('rationale')); state['events'][-1]['text']+=f' [AI: {p}]'
 _passive(state); state['history'].append({'turn':state['turn'],'countries':copy.deepcopy(state['countries'])}); return state
def player_intervention(state,country,action,target=None):
 apply_action(state,country,action,target,'Player intervention.'); _event(state,'player',f'PLAYER INTERVENTION: ordered {country} to {action.replace("_"," ")}.'); return state

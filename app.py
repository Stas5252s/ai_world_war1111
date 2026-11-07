import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from worldwar.engine import new_world,advance_turn,player_intervention,ensure_organizations,organization_membership
from worldwar.data import ACTION_LABELS
from worldwar.intelligence import explain_question
st.set_page_config(page_title='AI WORLD WAR',page_icon='🌍',layout='wide')
if 'world' not in st.session_state: st.session_state.world=new_world()
world=st.session_state.world; countries=world['countries']
ensure_organizations(world)
world.setdefault('sovereignty',{n:n for n in countries})
for n in countries: world['sovereignty'].setdefault(n,n)
sovereignty=world['sovereignty']
independent_countries=[n for n in countries if sovereignty.get(n,n)==n]
territory_counts={n:sum(1 for owner in sovereignty.values() if owner==n) for n in countries}
annexed_territories=sum(1 for territory,owner in sovereignty.items() if territory!=owner)
st.markdown('<style>.block-container{padding-top:1.2rem}div[data-testid="stMetric"]{background:rgba(120,120,120,.08);padding:12px;border-radius:10px}</style>',unsafe_allow_html=True)
st.title('🌍 AI WORLD WAR'); st.caption('Autonomous geopolitical sandbox · MVP 0.1 · Fictional game abstractions')
with st.sidebar:
 st.header('Simulation control'); st.metric('Current turn',world['turn'])
 if st.button('▶ Advance one turn',type='primary',use_container_width=True):
  cfg={n:{'provider':st.session_state.get('provider_'+n,'Fallback'),'model':st.session_state.get('model_'+n,'')} for n in countries}
  with st.spinner('Governments are making decisions...'): advance_turn(world,cfg)
  st.rerun()
 batch_turns=st.number_input('Number of turns to simulate',min_value=1,max_value=500,value=10,step=1)
 if st.button('⏩ Simulate turns',use_container_width=True):
  cfg={n:{'provider':st.session_state.get('provider_'+n,'Fallback'),'model':st.session_state.get('model_'+n,'')} for n in countries}
  progress=st.progress(0)
  status=st.empty()
  for i in range(int(batch_turns)):
   advance_turn(world,cfg)
   progress.progress((i+1)/int(batch_turns))
   status.caption(f"Simulated {i+1} / {int(batch_turns)} turns")
  st.rerun()
 if st.button('↻ Reset world',use_container_width=True): st.session_state.world=new_world(); st.rerun()
 st.divider(); st.subheader('Default provider')
 dp=st.selectbox('Provider for all', ['Fallback','Ollama','Cloud API']); dm=st.text_input('Default model',placeholder='qwen2.5:3b')
 if st.button('Apply to all countries'):
  for n in countries: st.session_state['provider_'+n]=dp; st.session_state['model_'+n]=dm
  st.success('Settings applied.')
cols=st.columns(4); cols[0].metric('Sovereign states',len(independent_countries)); cols[1].metric('Annexed territories',annexed_territories); cols[2].metric('World GDP (USD T)',f"{sum(c['gdp'] for c in countries.values()):.2f}"); cols[3].metric('Active wars',sum(1 for w in world.get('wars',{}).values() if w.get('status')=='active'))
tmap,tc,tx,td,te,twi,tn,tpol,tp,ta,ti,th=st.tabs(['🌐 World map','📊 Countries','💹 Economy','🤝 Diplomacy','📰 World events','🧠 Intelligence','🌍 World News','🏛️ Politics','🎮 Player intervention','🤖 AI agents','🌐 Influence','📈 History'])
with tmap:
 influence_data=world.get('influence',{})
 influence_leaders={}
 for target in countries:
  scores=influence_data.get(target,{})
  leader,score=max(scores.items(),key=lambda item:item[1]) if scores else ('No dominant influence',0)
  influence_leaders[target]=(leader if score>=12 else 'No dominant influence',score)
 df=pd.DataFrame([{'Country':n,'ISO':c['iso'],'GDP':c['gdp'],'Stability':c['stability'],'Military':c['military'],'Controller':sovereignty.get(n,n),'Influence leader':influence_leaders[n][0],'Influence score':influence_leaders[n][1]} for n,c in countries.items()])
 map_mode=st.radio('Map layer',['Stability','Territorial control','Influence'],horizontal=True)
 if map_mode=='Territorial control':
  fig=px.choropleth(df,locations='ISO',color='Controller',hover_name='Country',hover_data={'Controller':True,'GDP':':.3f','Stability':':.1f','Military':':.1f','ISO':False},color_discrete_sequence=px.colors.qualitative.Dark24,projection='natural earth',title='Territorial control · simulated ownership')
 elif map_mode=='Influence':
  fig=px.choropleth(df,locations='ISO',color='Influence leader',hover_name='Country',hover_data={'Influence leader':True,'Influence score':':.1f','Controller':True,'ISO':False},color_discrete_sequence=px.colors.qualitative.Dark24,projection='natural earth',title='Leading foreign influence · simulated soft power')
 else:
  fig=px.choropleth(df,locations='ISO',color='Stability',hover_name='Country',hover_data={'Controller':True,'GDP':':.3f','Stability':':.1f','Military':':.1f','ISO':False},color_continuous_scale='RdYlGn',range_color=(0,100),projection='natural earth',title='National stability · simulated values')
 coords={n:(c['lon'],c['lat']) for n,c in countries.items() if c.get('lon') is not None and c.get('lat') is not None}
 active_wars=[w for w in world.get('wars',{}).values() if w.get('status')=='active']
 for war in active_wars:
  for side_key,side_name,color,symbol in [('side_a','Side A','#2878d0','circle'),('side_b','Side B','#e34b4b','diamond')]:
   members=[n for n in war.get(side_key,[]) if n in coords]
   if members:
    fig.add_trace(go.Scattergeo(lon=[coords[n][0] for n in members],lat=[coords[n][1] for n in members],text=members,mode='markers+text',textposition='top center',marker=dict(size=11,color=color,symbol=symbol,line=dict(width=1,color='white')),name=f"War {war.get('id','?')} · {side_name}",hovertemplate=f"War {war.get('id','?')}<br>{side_name}: %{{text}}<extra></extra>"))
 fig.update_layout(height=570,margin=dict(l=0,r=0,t=50,b=0),paper_bgcolor='rgba(0,0,0,0)',geo=dict(bgcolor='rgba(0,0,0,0)'),legend=dict(title='War sides',orientation='h',yanchor='bottom',y=-0.12,x=0))
 st.plotly_chart(fig,use_container_width=True)
 if active_wars:
  st.markdown('### Active wars')
  st.caption('Blue circles = Side A. Red diamonds = Side B. Country fill = stability.')
  for war in active_wars:
   side_a=[n for n in war.get('side_a',[]) if n in countries]
   side_b=[n for n in war.get('side_b',[]) if n in countries]
   progress=float(war.get('progress',50))
   with st.container(border=True):
    st.markdown(f"**War {war.get('id','?')}**")
    left,right=st.columns(2)
    with left:
     st.markdown('**SIDE A**')
     st.write(', '.join(side_a) if side_a else 'No participants listed')
    with right:
     st.markdown('**SIDE B**')
     st.write(', '.join(side_b) if side_b else 'No participants listed')
    st.progress(max(0,min(100,int(progress))))
    st.caption(f"War progress: {progress:.0f}%")
    changes=war.get('territory_changes',[])
    if changes:
     st.markdown('**Recent frontline changes**')
     for change in reversed(changes[-4:]):
      st.caption(f"Turn {change['turn']}: {change['territory']} · {change['from']} → {change['to']}")
 else:
  st.info('No active wars right now. Rivalries can escalate as the simulation advances.')
 st.caption('Synthetic game values, not real-world assessments.')
with tc:
 rows=[{'Country':n,'Controller':sovereignty.get(n,n),'Status':'Independent' if sovereignty.get(n,n)==n else 'Annexed','Territories controlled':territory_counts.get(n,0),'Population (M)':c['population'],'GDP (USD T)':c['gdp'],'Stability':c['stability'],'Technology':c['tech'],'Military':c['military'],'Resources':c['resources'],'Budget (USD bn)':c.get('budget',0),'Treasury (USD bn)':c.get('treasury',0),'Debt (USD bn)':c.get('debt',0),'Production':c.get('production',0),'Trade (USD bn)':c.get('trade',0)} for n,c in countries.items()]
 st.dataframe(pd.DataFrame(rows).set_index('Country').style.format(precision=1),use_container_width=True)
 selected=st.selectbox('Inspect country',list(countries)); c=countries[selected]; st.subheader(selected)
 worldview=c.get('worldview',{})
 if worldview:
  with st.expander('Strategic worldview',expanded=True):
   st.markdown('**World outlook**')
   st.write(worldview.get('outlook',''))
   st.markdown('**Main priorities**')
   st.write(' · '.join(worldview.get('priorities',[])))
   st.markdown('**Red lines**')
   st.write(' · '.join(worldview.get('red_lines',[])))
   st.markdown('**Preferred partners**')
   st.write(', '.join(worldview.get('preferred_partners',[])) or 'No fixed preferred partners')
   st.markdown('**Strategic competitors**')
   st.write(', '.join(worldview.get('competitors',[])) or 'No fixed strategic competitors')
   st.caption('Strategic posture: '+worldview.get('posture','Pragmatic national-development policy'))
 else:
  st.caption('This country uses a general pragmatic doctrine.')
 m=st.columns(4)
 for col,label,key in zip(m,['GDP','Stability','Technology','Military'],['gdp','stability','tech','military']): col.metric(label,f"{c[key]:.2f}")
 rdf=pd.DataFrame([{'Country':n,'Relations':v} for n,v in world['relations'][selected].items() if n!=selected]); st.bar_chart(rdf.set_index('Country'))
with tx:
 st.subheader('National economy')
 st.caption('GDP is shown in USD trillions. Budgets, public debt and trade are in USD billions. Each turn represents one simulated year.')
 ec=st.columns(4)
 ec[0].metric('World GDP',f"${sum(c['gdp'] for c in countries.values()):.2f}T")
 ec[1].metric('Government revenue',f"${sum(c.get('budget',0) for c in countries.values()):,.0f}B")
 ec[2].metric('Trade volume',f"${sum(c.get('trade',0) for c in countries.values()):,.0f}B")
 ec[3].metric('Public debt',f"${sum(c.get('debt',0) for c in countries.values()):,.0f}B")
 econ_rows=[{'Country':n,'GDP (USD T)':c['gdp'],'GDP per capita (USD)':c['gdp']*1000000/c['population'],'Population (M)':c['population'],'Budget revenue (USD bn)':c.get('budget',0),'Budget balance (USD bn)':c.get('budget_balance',0),'Treasury (USD bn)':c.get('treasury',0),'Public debt (USD bn)':c.get('debt',0),'Resources':c['resources'],'Resource stock':c.get('resource_stock',0),'Production index':c.get('production',0),'Trade volume (USD bn)':c.get('trade',0),'Trade balance (USD bn)':c.get('trade_balance',0),'Inflation %':c.get('inflation',0),'Unemployment %':c.get('unemployment',0)} for n,c in countries.items()]
 st.dataframe(pd.DataFrame(econ_rows).set_index('Country').style.format(precision=2),use_container_width=True,height=520)
 top=sorted(countries.items(),key=lambda item:item[1]['gdp'],reverse=True)[:15]
 top_df=pd.DataFrame([{'Country':n,'GDP (USD T)':c['gdp']} for n,c in top])
 st.markdown('### Largest economies')
 st.plotly_chart(px.bar(top_df,x='GDP (USD T)',y='Country',orientation='h',title='Top 15 economies by nominal GDP',height=520),use_container_width=True)
 econ_country=st.selectbox('Inspect economic indicators',list(countries),key='economy_country')
 ecountry=countries[econ_country]
 st.markdown(f"### {econ_country}")
 em=st.columns(4)
 em[0].metric('GDP',f"${ecountry['gdp']:.3f}T")
 em[1].metric('Annual budget balance',f"${ecountry.get('budget_balance',0):,.1f}B")
 em[2].metric('Public debt',f"${ecountry.get('debt',0):,.1f}B")
 em[3].metric('Production index',f"{ecountry.get('production',0):.1f}/100")
 st.caption(f"Population: {ecountry['population']:.2f} million · Resources: {ecountry['resources']:.0f}/100 · Stock: {ecountry.get('resource_stock',0):.1f}/100 · Inflation: {ecountry.get('inflation',0):.1f}% · Unemployment: {ecountry.get('unemployment',0):.1f}%")

with td:
 st.subheader('Diplomatic landscape')
 blocs=world.get('blocs',{})
 guarantees=world.get('guarantees',[])
 agreements=world.get('trade_agreements',[])
 ultimatums=[u for u in world.get('ultimatums',[]) if u.get('status')=='pending']
 sanctions=world.get('sanctions',[])
 alliances=world.get('alliances',{})
 alliance_pairs=sorted({tuple(sorted((a,b))) for a,members in alliances.items() for b in members if a in countries and b in countries and a in alliances.get(b,[])})
 dc=st.columns(5)
 dc[0].metric('Mutual alliances',len(alliance_pairs))
 dc[1].metric('International blocs',len(blocs))
 dc[2].metric('Trade agreements',len(agreements))
 dc[3].metric('Independence guarantees',len(guarantees))
 dc[4].metric('Active sanctions',len(sanctions))
 st.markdown('### Mutual-defense alliances')
 st.caption('These are formal bilateral military alliances. Allies may automatically join a partner\'s side if a war starts.')
 if alliance_pairs:
  alliance_rows=[]
  for a,b in alliance_pairs:
   shared_wars=[w.get('id') for w in world.get('wars',{}).values() if w.get('status')=='active' and a in w.get('participants',[]) and b in w.get('participants',[])]
   alliance_rows.append({'Country A':a,'Country B':b,'Relations':world.get('relations',{}).get(a,{}).get(b,0),'At war together':bool(shared_wars)})
  st.dataframe(pd.DataFrame(alliance_rows),hide_index=True,use_container_width=True)
  alliance_country=st.selectbox('Inspect a country\'s alliances',list(countries),key='alliance_inspect_country')
  allies=sorted([n for n in alliances.get(alliance_country,[]) if n in countries and alliance_country in alliances.get(n,[])])
  if allies:
   st.markdown(f'**{alliance_country} is allied with {len(allies)} countries:**')
   for ally in allies:
    relation=world.get('relations',{}).get(alliance_country,{}).get(ally,0)
    current_war=next((w for w in world.get('wars',{}).values() if w.get('status')=='active' and alliance_country in w.get('participants',[]) and ally in w.get('participants',[])),None)
    status=f' · fighting together in War #{current_war.get("id")}' if current_war else ''
    st.write(f'• **{ally}** · relations {relation:+.0f}/100{status}')
  else:
   st.info(f'{alliance_country} has no active mutual-defense alliances.')
 else:
  st.info('No mutual-defense alliances have formed yet. Governments can create them as the simulation advances.')
 st.markdown('### International organizations')
 organizations=ensure_organizations(world)
 org_rows=[]
 for org_id,org in organizations.items():
  org_rows.append({'Organization':org['name'],'Type':org.get('type','diplomatic').title(),'Members':len(org.get('members',[])),'Membership':', '.join(org.get('members',[]))})
 st.dataframe(pd.DataFrame(org_rows).set_index('Organization'),use_container_width=True)
 org_id=st.selectbox('Inspect organization',list(organizations),format_func=lambda key:organizations[key]['name'],key='inspect_organization')
 org=organizations[org_id]
 st.markdown(f"**{org['name']}**")
 st.write(org.get('description',''))
 st.caption(f"Category: {org.get('type','diplomatic').title()} · Members: {len(org.get('members',[]))}")
 members=org.get('members',[])
 if members:
  st.write(', '.join(sorted(members)))
 else:
  st.caption('No members.')
 st.markdown('#### Manage membership')
 member_country=st.selectbox('Country',independent_countries,key='organization_country') if independent_countries else None
 if member_country:
  left,right=st.columns(2)
  with left:
   if st.button('Join organization',use_container_width=True,disabled=member_country in members,key='join_org'):
    organization_membership(world,member_country,org_id,'join')
    st.rerun()
  with right:
   if st.button('Leave organization',use_container_width=True,disabled=member_country not in members,key='leave_org'):
    organization_membership(world,member_country,org_id,'leave')
    st.rerun()
 st.caption('Membership changes are player interventions. Collective defence and economic cooperation are applied by the simulation.')
 st.markdown('### International blocs')
 if blocs:
  for bloc in blocs.values():
   st.write(f"**{bloc['name']}** · Leader: {bloc['leader']} · Members: {', '.join(bloc['members'])}")
 else: st.caption('No international blocs have been founded yet.')
 st.markdown('### Trade agreements')
 if agreements:
  for deal in agreements: st.write(' ↔ '.join(deal.get('countries',[])))
 else: st.caption('No active trade agreements.')
 st.markdown('### Guarantees of independence')
 if guarantees:
  for guarantee in guarantees: st.write(f"{guarantee['guarantor']} guarantees {guarantee['protected']}")
 else: st.caption('No active guarantees.')
 st.markdown('### Active sanctions')
 if sanctions:
  for sanction in sanctions: st.warning(f"{sanction['issuer']} → {sanction['target']} · trade and GDP growth restricted")
 else: st.caption('No active sanctions.')
 st.markdown('### Pending ultimatums')
 if ultimatums:
  for u in ultimatums: st.warning(f"{u['issuer']} → {u['target']} · expires on turn {u['expires']}")
 else: st.caption('No pending ultimatums.')
with te:
 st.subheader('World chronicle')
 for e in reversed(world['events'][-60:]):
  st.markdown(f"**TURN {e['turn']} · {e['kind'].upper()}**  \n{e['text']}")
  if e.get('rationale'): st.caption('AI rationale: '+e['rationale'])
with twi:
 st.subheader('Ask the world')
 st.caption('Ask why something happened. The report searches the simulation state, diplomacy, economy, wars and recorded events.')
 question=st.text_input('Ask the world',placeholder='Why did China and India become enemies?',key='world_question')
 if st.button('Investigate',type='primary',key='investigate_world') and question.strip():
  st.session_state['world_intelligence_result']=explain_question(world,question)
 report=st.session_state.get('world_intelligence_result')
 if report:
  st.markdown(f"### {report.get('title','Investigation')}")
  st.write(report.get('summary',''))
  causes=report.get('causes',[])
  if causes:
   st.markdown('#### What the simulation shows')
   for cause in causes:
    st.markdown(f"- {cause}")
  evidence=report.get('evidence',[])
  if evidence:
   st.markdown('#### Supporting event history')
   for item in evidence:
    st.markdown(f"- {item}")
  st.caption(report.get('confidence',''))
 st.divider()
 st.subheader('World News')

 st.caption('Headlines are generated from events that actually happened in this simulation.')
 events=list(reversed(world.get('events',[])))
 if events:
  featured=events[0]
  st.markdown(f"## {featured.get('text','')}")
  st.caption(f"TURN {featured.get('turn',0)} · {featured.get('kind','world').upper()}")
  st.divider()
  news_filter=st.multiselect('Filter news categories',sorted({e.get('kind','world') for e in events}),default=[])
  filtered=[e for e in events if not news_filter or e.get('kind','world') in news_filter]
  for event in filtered[:80]:
   with st.container(border=True):
    st.caption(f"TURN {event.get('turn',0)} · {event.get('kind','world').upper()}")
    st.markdown(f"**{event.get('text','')}**")
    if event.get('rationale'):
     st.caption(event['rationale'])
 else:
  st.info('No news yet. Advance the simulation to generate the first headlines.')

with tpol:
 st.subheader('Domestic politics')
 st.caption('Fictional political systems. Approval, elections and government changes evolve with each simulated year.')
 politics=world.get('politics',{})
 if not politics:
  st.info('Political profiles will be initialized on the next turn.')
 else:
  political_rows=[]
  for name,government in politics.items():
   if name in countries and sovereignty.get(name,name)==name:
    political_rows.append({'Country':name,'Government':government.get('government','—'),'Ideology':government.get('ideology','—'),'Approval (%)':government.get('approval',0),'Next election':government.get('election_due',0),'Elections held':government.get('elections',0)})
  political_df=pd.DataFrame(political_rows).sort_values('Approval (%)')
  st.markdown('### Governments under pressure')
  st.dataframe(political_df,hide_index=True,use_container_width=True,height=430)
  political_country=st.selectbox('Inspect domestic politics',list(countries),key='politics_country')
  government=politics.get(political_country,{})
  if government:
   st.markdown(f"### {political_country}")
   metrics=st.columns(4)
   metrics[0].metric('Government',government.get('government','—'))
   metrics[1].metric('Approval',f"{government.get('approval',0):.1f}%")
   metrics[2].metric('Opposition',government.get('opposition','—'))
   metrics[3].metric('Next election',f"Turn {government.get('election_due','—')}")
   st.write(f"**Ideology:** {government.get('ideology','—')}")
   st.write(f"**Elections held:** {government.get('elections',0)}")
   st.caption('Election outcomes and political approval are simulated, not predictions about real governments.')

with tp:
 st.subheader('Direct intervention'); st.write('Issue a game-level policy order to any government.')
 if not independent_countries:
  st.warning('No independent states remain. Reset the world to start a new simulation.')
 else:
  country=st.selectbox('Country',independent_countries,key='player_country'); action=st.selectbox('Order',list(ACTION_LABELS),format_func=lambda x:ACTION_LABELS[x]); target=None
  if action in ['diplomacy','trade','deescalate','sanction','conflict','declare_war','form_alliance','break_alliance','peace','continue_war','guarantee_independence','revoke_guarantee','ultimatum','accept_ultimatum','reject_ultimatum','sever_relations','invite_to_bloc']:
   target=st.selectbox('Target',[n for n in independent_countries if n!=country])
  if st.button('Execute intervention',type='primary'): player_intervention(world,country,action,target); st.success('Intervention recorded.'); st.rerun()
 st.info('Conflict is an abstract game contest. No real-world tactics or operational military guidance are modelled.')
with ta:
 st.subheader('Configure individual presidents'); st.caption('Fallback works offline. Ollama runs locally. Cloud API requires credentials.')
 agent_country=st.selectbox('Country to configure',list(countries),key='agent_country')
 with st.container(border=True):
  st.selectbox('Provider',['Fallback','Ollama','Cloud API'],key='provider_'+agent_country)
  st.text_input('Model override',key='model_'+agent_country,placeholder='Use environment default')
  st.caption('Profile: '+countries[agent_country]['style'])
  st.caption('Economic profile: GDP '+str(round(countries[agent_country]['gdp'],3))+'T · production '+str(round(countries[agent_country].get('production',0),1))+'/100')
with ti:
 st.subheader('Global spheres of influence')
 st.caption('Influence is a fictional soft-power index. It changes through diplomatic relations, trade, alliances, blocs, guarantees, sanctions and abstract conflict. It is not a real-world measurement.')
 influence_data=world.get('influence',{})
 if not influence_data:
  st.info('Influence tracking will begin after the next simulated turn.')
 else:
  totals={}
  for target,scores in influence_data.items():
   if target in independent_countries:
    for actor,value in scores.items():
     if actor != target and actor in independent_countries:
      totals[actor]=totals.get(actor,0)+float(value)
  ranking=sorted(totals.items(),key=lambda item:item[1],reverse=True)
  top=st.columns(4)
  top[0].metric('Countries tracked',len(influence_data))
  top[1].metric('Influence centers',sum(1 for value in totals.values() if value>=100))
  top[2].metric('Leading power',ranking[0][0] if ranking else '—')
  top[3].metric('Influence score',f"{ranking[0][1]:,.1f}" if ranking else '0')
  if ranking:
   rank_df=pd.DataFrame([{'Power':name,'Total influence':value} for name,value in ranking[:15]])
   st.markdown('### Leading influence networks')
   st.plotly_chart(px.bar(rank_df,x='Total influence',y='Power',orientation='h',title='Aggregate foreign influence across independent states'),use_container_width=True)
  st.markdown('### Who influences a country?')
  influence_target=st.selectbox('Select country',list(countries),key='influence_target')
  target_scores=influence_data.get(influence_target,{})
  target_rows=sorted([{'Power':name,'Influence':value,'Relations':world.get('relations',{}).get(influence_target,{}).get(name,0)} for name,value in target_scores.items() if name in countries],key=lambda item:item['Influence'],reverse=True)
  if target_rows:
   target_df=pd.DataFrame(target_rows[:15])
   st.plotly_chart(px.bar(target_df,x='Influence',y='Power',orientation='h',title=f'Foreign influence in {influence_target}'),use_container_width=True)
   leader=target_rows[0]
   if leader['Influence']>=12:
    st.info(f"Leading external influence: {leader['Power']} · {leader['Influence']:.1f}/100")
   else:
    st.caption('No foreign power has established a dominant influence position yet.')
   st.dataframe(pd.DataFrame(target_rows),hide_index=True,use_container_width=True)
  else:
   st.caption('No foreign influence data for this country yet.')
with th:
 st.subheader('Simulation history')
 st.caption('One turn represents one simulated year. History starts at turn 0 and is recorded after every completed turn.')
 history=world.get('history',[])
 if not history:
  st.info('No historical snapshots yet. Advance the simulation to start building its timeline.')
 else:
  history_rows=[]
  for snapshot in history:
   snapshot_countries=snapshot.get('countries',{})
   world_gdp=snapshot.get('world_gdp')
   world_population=snapshot.get('world_population')
   if world_gdp is None:
    world_gdp=sum(v.get('gdp',0) for v in snapshot_countries.values() if isinstance(v,dict))
   if world_population is None:
    world_population=sum(v.get('population',0) for v in snapshot_countries.values() if isinstance(v,dict))
   old_wars=snapshot.get('wars',{})
   active_wars=snapshot.get('active_wars')
   if active_wars is None:
    active_wars=sum(1 for w in old_wars.values() if w.get('status')=='active') if isinstance(old_wars,dict) else 0
   old_sovereignty=snapshot.get('sovereignty',{})
   sovereign_states=snapshot.get('sovereign_states')
   if sovereign_states is None:
    sovereign_states=sum(1 for country_name,owner in old_sovereignty.items() if country_name==owner) if old_sovereignty else len(countries)
   history_rows.append({'Turn':snapshot.get('turn',0),'World GDP (USD T)':world_gdp,'World population (M)':world_population,'Active wars':active_wars,'Sovereign states':sovereign_states})
  history_df=pd.DataFrame(history_rows).sort_values('Turn').drop_duplicates('Turn',keep='last')
  st.markdown('### World timeline')
  world_metric=st.selectbox('World indicator',['World GDP (USD T)','World population (M)','Active wars','Sovereign states'],key='world_history_metric')
  st.line_chart(history_df.set_index('Turn')[[world_metric]],use_container_width=True)
  first=history_df.iloc[0]
  latest=history_df.iloc[-1]
  k=st.columns(4)
  k[0].metric('World GDP',f"${latest['World GDP (USD T)']:.2f}T",f"{latest['World GDP (USD T)']-first['World GDP (USD T)']:+.2f}T since start")
  k[1].metric('Population',f"{latest['World population (M)']:,.1f}M",f"{latest['World population (M)']-first['World population (M)']:+,.1f}M")
  k[2].metric('Active wars',int(latest['Active wars']),f"{int(latest['Active wars'])-int(first['Active wars']):+d} since start")
  k[3].metric('Sovereign states',int(latest['Sovereign states']),f"{int(latest['Sovereign states'])-int(first['Sovereign states']):+d} since start")
  st.divider()
  st.markdown('### Country development')
  history_country=st.selectbox('Country',list(countries),key='history_country')
  country_metric=st.selectbox('Indicator',['GDP (USD bn)','Population (M)','Stability','Technology','Military','Production'],key='country_history_metric')
  country_rows=[]
  for snapshot in history:
   data=snapshot.get('countries',{}).get(history_country,{})
   if isinstance(data,dict) and data:
    value=data.get('gdp',0)*1000 if country_metric=='GDP (USD bn)' else data.get({'Population (M)':'population','Stability':'stability','Technology':'tech','Military':'military','Production':'production'}[country_metric],0)
    country_rows.append({'Turn':snapshot.get('turn',0),country_metric:value})
  if country_rows:
   country_df=pd.DataFrame(country_rows).sort_values('Turn').drop_duplicates('Turn',keep='last')
   st.line_chart(country_df.set_index('Turn')[[country_metric]],use_container_width=True)
   start_value=country_df.iloc[0][country_metric]
   current_value=country_df.iloc[-1][country_metric]
   delta=current_value-start_value
   st.metric(f'{history_country} · {country_metric}',f'{current_value:,.3f}',f'{delta:+,.3f} since start')
  else:
   st.info('This country has no compatible historical data yet. New snapshots will appear after the next turn.')
  st.markdown('### Recorded turns')
  st.dataframe(history_df.set_index('Turn'),use_container_width=True)

st.divider(); st.caption('Population and GDP baselines use 2024 data where available; stability, military, technology and resource indices are game estimates.')

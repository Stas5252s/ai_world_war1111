import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from worldwar.engine import new_world,advance_turn,player_intervention
from worldwar.data import ACTION_LABELS
st.set_page_config(page_title='AI WORLD WAR',page_icon='🌍',layout='wide')
if 'world' not in st.session_state: st.session_state.world=new_world()
world=st.session_state.world; countries=world['countries']
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
cols=st.columns(4); cols[0].metric('Sovereign states',len(independent_countries)); cols[1].metric('Annexed territories',annexed_territories); cols[2].metric('Combined GDP (game units)',f"{sum(c['gdp'] for c in countries.values()):.2f}"); cols[3].metric('Active wars',sum(1 for w in world.get('wars',{}).values() if w.get('status')=='active'))
tmap,tc,tx,td,te,tp,ta=st.tabs(['🌐 World map','📊 Countries','💹 Economy','🤝 Diplomacy','📰 World events','🎮 Player intervention','🤖 AI agents'])
with tmap:
 df=pd.DataFrame([{'Country':n,'ISO':c['iso'],'GDP':c['gdp'],'Stability':c['stability'],'Military':c['military'],'Controller':sovereignty.get(n,n)} for n,c in countries.items()])
 map_mode=st.radio('Map layer',['Stability','Territorial control'],horizontal=True)
 if map_mode=='Territorial control':
  fig=px.choropleth(df,locations='ISO',color='Controller',hover_name='Country',hover_data={'Controller':True,'GDP':':.3f','Stability':':.1f','Military':':.1f','ISO':False},color_discrete_sequence=px.colors.qualitative.Dark24,projection='natural earth',title='Territorial control · simulated ownership')
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
 rows=[{'Country':n,'Controller':sovereignty.get(n,n),'Status':'Independent' if sovereignty.get(n,n)==n else 'Annexed','Territories controlled':territory_counts.get(n,0),'Population (M)':c['population'],'GDP (game units)':c['gdp'],'Stability':c['stability'],'Technology':c['tech'],'Military':c['military'],'Resources':c['resources'],'Budget (USD bn)':c.get('budget',0),'Treasury (USD bn)':c.get('treasury',0),'Debt (USD bn)':c.get('debt',0),'Production':c.get('production',0),'Trade (USD bn)':c.get('trade',0)} for n,c in countries.items()]
 st.dataframe(pd.DataFrame(rows).set_index('Country').style.format(precision=1),use_container_width=True)
 selected=st.selectbox('Inspect country',list(countries)); c=countries[selected]; st.subheader(selected); m=st.columns(4)
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
 dc=st.columns(3)
 dc[0].metric('International blocs',len(blocs))
 dc[1].metric('Trade agreements',len(agreements))
 dc[2].metric('Independence guarantees',len(guarantees))
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
 st.markdown('### Pending ultimatums')
 if ultimatums:
  for u in ultimatums: st.warning(f"{u['issuer']} → {u['target']} · expires on turn {u['expires']}")
 else: st.caption('No pending ultimatums.')
with te:
 st.subheader('World chronicle')
 for e in reversed(world['events'][-60:]):
  st.markdown(f"**TURN {e['turn']} · {e['kind'].upper()}**  \n{e['text']}")
  if e.get('rationale'): st.caption('AI rationale: '+e['rationale'])
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
st.divider(); st.caption('Synthetic starting attributes. Not live statistics, intelligence or forecasts.')

import streamlit as st
import pandas as pd
import plotly.express as px
from worldwar.engine import new_world,advance_turn,player_intervention
from worldwar.data import ACTION_LABELS
st.set_page_config(page_title='AI WORLD WAR',page_icon='🌍',layout='wide')
if 'world' not in st.session_state: st.session_state.world=new_world()
world=st.session_state.world; countries=world['countries']
st.markdown('<style>.block-container{padding-top:1.2rem}div[data-testid="stMetric"]{background:rgba(120,120,120,.08);padding:12px;border-radius:10px}</style>',unsafe_allow_html=True)
st.title('🌍 AI WORLD WAR'); st.caption('Autonomous geopolitical sandbox · MVP 0.1 · Fictional game abstractions')
with st.sidebar:
 st.header('Simulation control'); st.metric('Current turn',world['turn'])
 if st.button('▶ Advance one turn',type='primary',use_container_width=True):
  cfg={n:{'provider':st.session_state.get('provider_'+n,'Fallback'),'model':st.session_state.get('model_'+n,'')} for n in countries}
  with st.spinner('Governments are making decisions...'): advance_turn(world,cfg)
  st.rerun()
 if st.button('↻ Reset world',use_container_width=True): st.session_state.world=new_world(); st.rerun()
 st.divider(); st.subheader('Default provider')
 dp=st.selectbox('Provider for all', ['Fallback','Ollama','Cloud API']); dm=st.text_input('Default model',placeholder='qwen2.5:3b')
 if st.button('Apply to all countries'):
  for n in countries: st.session_state['provider_'+n]=dp; st.session_state['model_'+n]=dm
  st.success('Settings applied.')
cols=st.columns(4); cols[0].metric('Countries',len(countries)); cols[1].metric('Combined GDP (game units)',f"{sum(c['gdp'] for c in countries.values()):.2f}"); cols[2].metric('Average stability',f"{sum(c['stability'] for c in countries.values())/len(countries):.1f}/100"); cols[3].metric('Average technology',f"{sum(c['tech'] for c in countries.values())/len(countries):.1f}/100")
tmap,tc,te,tp,ta=st.tabs(['🌐 World map','📊 Countries','📰 World events','🎮 Player intervention','🤖 AI agents'])
with tmap:
 df=pd.DataFrame([{'Country':n,'ISO':c['iso'],'GDP':c['gdp'],'Stability':c['stability'],'Military':c['military']} for n,c in countries.items()])
 fig=px.choropleth(df,locations='ISO',color='Stability',hover_name='Country',hover_data={'GDP':':.3f','Stability':':.1f','Military':':.1f','ISO':False},color_continuous_scale='RdYlGn',range_color=(0,100),projection='natural earth',title='National stability · simulated values')
 fig.update_layout(height=550,margin=dict(l=0,r=0,t=50,b=0),paper_bgcolor='rgba(0,0,0,0)',geo=dict(bgcolor='rgba(0,0,0,0)')); st.plotly_chart(fig,use_container_width=True); st.caption('Synthetic game values, not real-world assessments.')
with tc:
 rows=[{'Country':n,'Population (M)':c['population'],'GDP (game units)':c['gdp'],'Stability':c['stability'],'Technology':c['tech'],'Military':c['military'],'Resources':c['resources']} for n,c in countries.items()]
 st.dataframe(pd.DataFrame(rows).set_index('Country').style.format(precision=1),use_container_width=True)
 selected=st.selectbox('Inspect country',list(countries)); c=countries[selected]; st.subheader(selected); m=st.columns(4)
 for col,label,key in zip(m,['GDP','Stability','Technology','Military'],['gdp','stability','tech','military']): col.metric(label,f"{c[key]:.2f}")
 rdf=pd.DataFrame([{'Country':n,'Relations':v} for n,v in world['relations'][selected].items() if n!=selected]); st.bar_chart(rdf.set_index('Country'))
with te:
 st.subheader('World chronicle')
 for e in reversed(world['events'][-60:]):
  st.markdown(f"**TURN {e['turn']} · {e['kind'].upper()}**  \n{e['text']}")
  if e.get('rationale'): st.caption('AI rationale: '+e['rationale'])
with tp:
 st.subheader('Direct intervention'); st.write('Issue a game-level policy order to any government.')
 country=st.selectbox('Country',list(countries),key='player_country'); action=st.selectbox('Order',list(ACTION_LABELS),format_func=lambda x:ACTION_LABELS[x]); target=None
 if action in ['diplomacy','trade','deescalate','sanction','conflict']: target=st.selectbox('Target',[n for n in countries if n!=country])
 if st.button('Execute intervention',type='primary'): player_intervention(world,country,action,target); st.success('Intervention recorded.'); st.rerun()
 st.info('Conflict is an abstract game contest. No real-world tactics or operational military guidance are modelled.')
with ta:
 st.subheader('Configure individual presidents'); st.caption('Fallback works offline. Ollama runs locally. Cloud API requires credentials.')
 for name in countries:
  with st.expander(name):
   st.selectbox('Provider',['Fallback','Ollama','Cloud API'],key='provider_'+name); st.text_input('Model override',key='model_'+name,placeholder='Use environment default')
   st.caption('Profile: '+countries[name]['style'])
st.divider(); st.caption('Synthetic starting attributes. Not live statistics, intelligence or forecasts.')

import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
from sklearn.externals import joblib
import plotly.graph_objs as go


data = pd.read_csv('countries.csv')
data['figure'] = ['{:,}'.format(v) for v in data.population]
countries = list(data.country.unique())
thresholds  = [max(data['population']), 200000000, 100000000, 10000000, 1000000, 100000, min(data['population']) ]
threshold_words =['maximum population', 'two hundred million', 'one hundred million', \
    'ten million', 'one million', 'one hundred thousand', 'minimum population']
   
    
def main():
    menu = ['Home', 'Predict', 'Map']
    Menu = st.sidebar.selectbox('Menu', menu)
    if Menu == 'Home':
        home()
    if Menu == 'Predict':
        predict()
    if Menu == 'Map':
        map(data)
        
        
def home():
    st.header('Countries population')
    st.markdown('> Graph a country\'s population between 1952 to 2007')
    
    country_name = st.selectbox('Country name', ['None Selected'] +list(data.country.unique()))
    if country_name != 'None Selected':
        df_bar = data[data.country == country_name]
        df_bar.year = df_bar.year.astype('str')
        plotly_chart = px.bar(data_frame = df_bar, x = 'year',
                              y = 'population', color = 'population',
                              hover_name = 'country',
                              width = 700, text = 'figure',
                              title = '{} population\'s chart'.format(country_name),)
        st.plotly_chart(plotly_chart, use_container_width= True)
    
    st.markdown('---')
    if st.checkbox('Graph by Year'):
        df1 = data
        df1.year = df1.year.astype('str')
        input_y = st.multiselect('Year', list(data.year.unique()))
        if len(input_y)  > 0:
            df1 = df1[df1.year.isin(input_y)]
        y_graph = alt.Chart(df1).transform_filter(alt.datum.population > 0).mark_line().encode(
            x = alt.X('country', title = 'Countries', type ='nominal'),
            y = alt.Y('population', title = 'Population'),
            color = 'year',
            tooltip = ['population','figure', 'year', 'country']).properties(
                width = 1200, height = 600).configure_axis(
                    labelFontSize =10, titleFontSize = 11)
        st.altair_chart(y_graph, )
        
        if st.checkbox('Population between...(Per year)'):
            for i in range(len(thresholds)-1):
                st.markdown('---')
                if st.checkbox('Population between {} and {} (Per year)'.format(
                    threshold_words[i], threshold_words[i+1]), key = str(i),):
                    country_set, dfy = get_data(i)
                    dfy.year = dfy.year.astype('str')
                    if st.button('View countries', key = str(i)):
                        st.write(tuple(country_set))
                    input_year = st.multiselect('Year', list(dfy['year'].unique()), key = str(i))
                    if len(input_year) > 0:
                        dfy = dfy[dfy.year.isin(input_year)]
                    graph = alt.Chart(dfy).transform_filter(alt.datum.population > 0).mark_line().encode(
                        x = alt.X('country', title = 'Countries', type = 'nominal'),
                        y = alt.Y('population', title ='Population'),
                        color ='year',
                        tooltip = ['population','figure', 'year', 'country']).properties(
                            width = 950, height =600).configure_axis(
                                labelFontSize = 10, titleFontSize = 11)
                    st.altair_chart(graph)
            st.markdown('---')
            st.markdown('---')
            
            
    if st.checkbox('Graph by country'):
        dff = data
        input_country = st.multiselect('Country name', list(data['country'].unique()))
        if len(input_country) > 0:
            dff = data[data.country.isin(input_country)]
        graph = alt.Chart(dff).transform_filter(alt.datum.population > 0).mark_line().encode(
            x = alt.X('year', title = 'Year', type = 'nominal'),
            y = alt.Y('population', title ='Population'),
            color ='country',
            tooltip = ['population','figure', 'year', 'country']).properties(
                width = 800, height =600).configure_axis(
                    labelFontSize = 10, titleFontSize = 11)
        st.altair_chart(graph)
        if st.checkbox('Population between...(Per Country)'):
            for i in range(len(thresholds)-1):
                st.markdown('---')
                if st.checkbox('Population between {} and {} (Per country)'.format(
                    threshold_words[i], threshold_words[i+1]), key = str(i)):
                    country_set, df = get_data(i)
                    if st.button('View countries', key = str(i)):
                        st.write(tuple(country_set))
                    country_input = st.multiselect(label ='Country name',key = str(i), options =list(country_set))
                    if len(country_input) > 0:
                        df = df[df.country.isin(country_input)]
                    pop_graph = alt.Chart(df).transform_filter(alt.datum.population > 0).mark_line().encode(
                        x = alt.X('year', title = 'Year', type = 'nominal'),
                        y = alt.Y('population', title ='Population'),
                        color ='country', 
                        tooltip = ['population','figure', 'year', 'country']).properties(
                            width = 800, height =600).configure_axis(
                                labelFontSize = 10, titleFontSize = 11)
                    st.altair_chart(pop_graph,)
             

def get_data(i):
    country_set = set()
    for idx, row in data.iterrows():
        if thresholds[i+1] < row[2] < thresholds[i]:
            country_set.add(row[0])
    country_drop = set(countries).difference(country_set)
    df_index = data.set_index('country')
    df_idx = df_index.drop(list(country_drop), axis= 0) 
    df = df_idx.reset_index(drop = False)
    return country_set, df
    
        
def predict():
    st.header('Countries Population')
    st.markdown('> Predict a country\'s population')
    st.markdown('---')
    year_list = list(range(2007, 2050, 5))
    country = st.selectbox('Select a country', ['None selected'] + countries)
    year = st.selectbox('Predict for year', year_list)
    
    if st.button('Predict population'):
        if country != 'None selected':
            if country and year:
                pred_data = pd.DataFrame([year], columns =['year'])
                model = joblib.load('country_model/' + country + '.pkl')
                resp = int(model.predict(pred_data))
                st.write('Population of {} in year {} is {:,}'.format(country, year, str(resp)))
                
    st.markdown('---')
    if st.checkbox('Generate past and future population figures with model'):
        country_gen = st.selectbox('Select a country', ['None selected'] + countries, key = str(200))
        year = st.slider(label = 'Year', min_value=1952, max_value=2050, value=(2000, 2007), step=5, )
        if st.checkbox('Generate'):
            if country_gen != 'None selected':
                if country_gen and year:
                    pred_data = pd.DataFrame(list(range(year[0], year[1], 3)), columns =['year'])
                    model = joblib.load('country_model/' + country + '.pkl')
                    resp = [int(v) for v in model.predict(pred_data)]
                    pred_data['country'] = ['country' for i in range(len(pred_data))]
                    pred_data['population'] = resp
                    st.dataframe(pred_data)
                    if st.button('Download data as csv file'):
                        pred_data.to_csv('generated_data.csv', index = False)
            else:
                st.error('Select a country!')
                    
    
def map(data):
    select_year = st.selectbox('Select year',list(data.year.unique()))
    df = data[data.year== select_year]
    data = dict(
        type = 'choropleth',
        locations = df['country'],
        locationmode = 'country names',
        colorscale = [[0, 'green'], [0.5, 'orange'], [1.0, 'red']],
        z = df['population'])
    plotly_map = go.Figure(data = [data])
    st.plotly_chart(plotly_map, use_container_width = True)
    if st.button('View countries'):
        st.write(tuple(df.country.unique()))

main()

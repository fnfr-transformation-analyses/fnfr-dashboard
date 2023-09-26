import pandas as pd
import plotly
import plotly_express as px
from slugify import slugify
from utils.utils import *

tableClasses = ['table', 'table-hover']

# #### Répartition des chercheurs (nombre de co-Pis, co-candidats, collaborateurs, etc.)
chercheurs  = pd.read_excel('data/fnfr_transformation_chercheur-e-s.xlsx')

def frequenceIndicateur(df: pd.DataFrame, variable: str) -> plotly.graph_objs._figure.Figure:
    indicateur = df[['Concours / Award', variable]]
    indicateur = indicateur.rename(columns = {variable: 'N'})
    indicateur = indicateur[['Concours / Award', 'N']]
    indicateur = indicateur.sort_values(by='N', ascending=False)

    table = []
    min = indicateur['N'].min()
    max = indicateur['N'].max()
    med = indicateur['N'].median().round(0).round(0).astype(int)
    moy = indicateur['N'].mean().round(2)
    ecartype = indicateur['N'].std().round(2)

    table.append({
        'min': min,
        'max': max,
        'médiane': med,
        'moyenne': moy,
        'écart-type': ecartype,
        'concours' : 'Tout'})


    tableFreq = []
    for i in range(min, max+1):
        for c in indicateur['Concours / Award'].unique():
            subdf = indicateur[indicateur['Concours / Award'] == c]
            n = len(subdf[subdf['N'] == i])
            tableFreq.append({'x': i, 'concours': str(c), 'n' : n})

            min = subdf['N'].min()
            max = subdf['N'].max()
            med = subdf['N'].median().round(0).astype(int)
            moy = subdf['N'].mean().round(2)
            ecartype = subdf['N'].std().round(2)

            table.append({
                'min': min,
                'max': max,
                'médiane': med,
                'moyenne': moy,
                'écart-type': ecartype,
                'concours' : c
            })

    tableFreq = pd.DataFrame(tableFreq)

    fig = px.bar(
        tableFreq, 
        x = 'x',
        y = 'n',
        color = 'concours',
        color_discrete_map={'2020': 'lightgrey', '2022': '#0b113a'},
        height = 300,
        barmode='group'
    )

    # Update layout to set white background
    fig.update_layout(
        plot_bgcolor='white',  # Set plot background color
        paper_bgcolor='white',  # Set paper (outside plot area) background color
        xaxis_title= variable,  # Hide x-axis title,
        xaxis=dict(tickangle=0),
        yaxis_title= 'N (projets)',  # Hide y-axis title,
        width=900
    )

    fig.update_traces(marker_line=dict(color='black', width=1))

    fig.update_yaxes(dtick=1)
    fig.update_xaxes(dtick=5)
    fig = fig.to_html(full_html=False, include_plotlyjs='cdn')

    table = pd.DataFrame(table)
    table = table.drop_duplicates()
    table = table.set_index('concours').reset_index().transpose()
    new_index = table.iloc[0]  #  first row as index
    table = table[1:]  # Remove the row that was used for the new index
    table.columns = new_index  
    table = table[[2020, 2022, 'Tout']].rename_axis(None, axis=1)
    table = table.to_html(classes = tableClasses, justify='left')

    return {'fig': fig, 'table': table}


repartitionChercheurs = {
    'Nombre de co-PIs (co-chercheurs principaux)' :frequenceIndicateur(chercheurs, 'N (CPIs)'),
    'Nombre de co-candidats' : frequenceIndicateur(chercheurs, 'N\n(co-candidats)'),
    'Nombre de collaborateurs' : frequenceIndicateur(chercheurs, 'N (Collaborators)'),
    "Taille totale de l'équipe" : frequenceIndicateur(chercheurs, 'N (Total)'),
}


#### Répartition géographique
## International 
# charger le mapping des pays qui sera utilisé pour construire la figure
mappingPays = pd.read_csv('utils/mapping_pays_iso.csv', sep=';', encoding='UTF-8').to_dict('records')
mappingPays = {x['Pays'] : x['Alpha-3 code'] for x in mappingPays}

# Charger les données
affiliations = pd.read_csv('data/affiliationsChercheurs.csv')
affiliations = affiliations[affiliations['Pays'] != '-']
affiliations['Code Alpha-3 Pays'] = affiliations['Pays'].map(mappingPays)

def generate_geo_figure(df: pd.DataFrame) -> plotly.graph_objs._figure.Figure:
    figPays = px.scatter_geo(
        df, 
        locations="Code Alpha-3 Pays",
        locationmode = 'ISO-3',
        hover_name = 'Pays',
        size="count",
        size_max = 50,
        height=440,
        projection = 'equirectangular',
        color_discrete_sequence=px.colors.qualitative.Prism,
    )

    # Customize the layout
    figPays.update_geos(
        showcoastlines=False,  # Hide coastlines/borders
        showland=True,  # Hide land area color
        landcolor = '#E8E8E8',
        showframe=True,  # Hide frame/borders
        projection_scale = 1.125,  # Adjust the projection scale to fit the map better
        center=dict(lon=20, lat=18),  # Set the center of the map to exclude Antarctica
    )

    figPays = figPays.update_layout( 
        margin=dict(t=0, l=0, r=0, b=0),
        title_x=0.2, 
    )

    return figPays

# Générer les figures
figs = []
tablesFreq = {}
mappingTables = {'count': 'N'}

# Figure - Tous les projets 
# Tableau de fréquence 
freqPays = pd.DataFrame(affiliations['Pays'].value_counts()).reset_index()
freqPays['Code Alpha-3 Pays'] = freqPays['Pays'].map(mappingPays)
freqPays = freqPays[['Pays', 'Code Alpha-3 Pays', 'count']]

with open('figures/geo/international/all.html', 'w') as f:
    f.write(generate_geo_figure(freqPays).to_html(full_html=False, include_plotlyjs='cdn'))

figs.append(
    {
        'Nom': 'Tout',
        'Fichier': 'figures/geo/international/all.html'
    }
)

# Create the table to display aside from the figure
tableF = freqPays.rename(columns = mappingTables)
tableF = tableF.sort_values(by=['N'], ascending=[False])[['Pays', 'N']]
tablesFreq[f"figures/geo/international/all.html"] = tableF.to_html(classes = tableClasses, justify='left', index=False)

# Figures - Par concours
freqPaysConcours = affiliations.groupby(['concours', 'Pays', 'Code Alpha-3 Pays'])['chercheur'].count().reset_index()
freqPaysConcours = freqPaysConcours.rename(columns={'chercheur': 'count'})

for c in freqPaysConcours['concours'].unique():
    subdf = freqPaysConcours[freqPaysConcours['concours'] == c]

    with open(f'figures/geo/international/{c}.html', 'w') as f:
        f.write(generate_geo_figure(subdf).to_html(full_html=False, include_plotlyjs='cdn'))

    figs.append(
        {
            'Nom': c,
            'Fichier': f'figures/geo/international/{c}.html'
        }
    ) 

    subdf = subdf[['Pays', 'count']].sort_values(by='count', ascending=False)
    
    # Create the table to display aside from the figure
    tableF = subdf.rename(columns = mappingTables)

    tableF = tableF.sort_values(by=['N'], ascending=[False])
    tablesFreq[f"figures/geo/international/{c}.html"] = tableF.to_html(classes = tableClasses, justify='left', index=False)

    # Figures - Par projet
    freqPaysProjets = affiliations.groupby(['projet', 'concours', 'Pays', 'Code Alpha-3 Pays'])['chercheur'].count().reset_index()
    freqPaysProjets = freqPaysProjets[freqPaysProjets['concours'] == c]
    freqPaysProjets = freqPaysProjets.rename(columns={'chercheur': 'count'})

    for p in freqPaysProjets['projet'].unique():
        slugifiedName = slugify(p)[:30]

        ssubdf = freqPaysProjets[freqPaysProjets['projet'] == p]

        with open(f'figures/geo/international/{slugifiedName}.html', 'w') as f:
            f.write(generate_geo_figure(ssubdf).to_html(full_html=False, include_plotlyjs='cdn'))

        figs.append(
            {
                'Nom': f"{c} -- {p}",
                'Fichier': f'figures/geo/international/{slugifiedName}.html'
            }
        ) 

        ssubdf = ssubdf[['Pays', 'count']].sort_values(by='count', ascending=False)
        
        # Create the table to display aside from the figure
        tableF = ssubdf.rename(columns = mappingTables)

        tableF = tableF.sort_values(by=['N'], ascending=[False])
        tablesFreq[f"figures/geo/international/{slugifiedName}.html"] = tableF.to_html(classes = tableClasses, justify='left', index=False)

tablesFreq = str(tablesFreq)

## Répartition géographique
## Canada 
## Répartition pancanadienne

# Create a scattergeo map with size of dots based on the 'count' column
def generate_geo_figure_provinces(df: pd.DataFrame) -> plotly.graph_objs._figure.Figure:
# Create a scattergeo map with size of dots based on the 'count' column
    figProvince = px.scatter_geo(
        df,
        lat='Latitude',
        lon='Longitude',
        size='count',
        color = 'Province',
        size_max = 50,
        color_discrete_sequence=px.colors.qualitative.Prism,
        projection='equirectangular',  # You can change the projection as needed
        hover_data={'Longitude':False,'Latitude':False}
    )

    # Customize the layout
    figProvince.update_geos(
        scope= 'world',
        showcoastlines=False,  # Hide coastlines/borders
        showland=True,  # Hide land area color
        showframe = True,
        landcolor = '#E8E8E8',
        center=dict(lon=-100, lat=60),  # Adjust lon and lat for centering
        lonaxis_range=[-140, -45],  # Adjust the range as needed for the desired zoom level
        lataxis_range=[40, 85],  # Adjust the range as needed for the desired zoom level
    )


    figProvince = figProvince.update_layout( 
        legend_title_text='',
        margin=dict(t=0, l=0, r=0, b=0),
        legend=dict(
        y=0,  # Adjust the y value to move the legend lower (0.0 is at the bottom)
        x=0.025,
        orientation='h', # Horizontal orientation
        entrywidth=130,
        font=dict(size=10)
        )
    )

    return figProvince

# Générer les figures
figsProvinces = []
tablesFreqProvinces = {}
mappingTables = {'count': 'N'}

# Figure - Tous les projets 
# Tableau de fréquence 
affiliationsCanada = affiliations[affiliations['Pays'] == 'Canada']
## Répartition pancanadienne
mapping_provinces = pd.read_csv('utils/mapping_provinces_canada_iso.csv')
mapping_provinces = mapping_provinces[mapping_provinces['Language code'] == 'fr']
mapping_provinces = {x['Subdivision name'] : x['3166-2 code'] for x in mapping_provinces.to_dict('records')}

province_info = pd.read_csv('utils/provinces_canada_coordinates.csv')
province_info['code-ISO province'] = province_info['Place Name'].map(mapping_provinces)
province_info = province_info.rename(columns={'Place Name': 'Province'})

affiliationsCanada = affiliations[affiliations['Pays'] == 'Canada']
affiliationsCanada = affiliationsCanada.merge(province_info, on='Province')

freqProvinces = pd.DataFrame(affiliationsCanada['Province'].value_counts()).reset_index()
freqProvinces = freqProvinces.merge(province_info, on='Province')

with open('figures/geo/canada/all.html', 'w') as f:
    f.write(generate_geo_figure_provinces(freqProvinces).to_html(full_html=False, include_plotlyjs='cdn'))

figsProvinces.append(
    {
        'Nom': 'Tout',
        'Fichier': 'figures/geo/canada/all.html'
    }
)

# Create the table to display aside from the figure
tableF = freqProvinces.rename(columns = mappingTables)
tableF = tableF.sort_values(by=['N'], ascending=[False])[['Province', 'N']]
tablesFreqProvinces[f"figures/geo/canada/all.html"] = tableF.to_html(classes = tableClasses, justify='left', index=False)

# Figures - Par concours
freqProvinceConcours = affiliationsCanada.groupby(['concours', 'Province', 'code-ISO province'])['chercheur'].count().reset_index()
freqProvinceConcours = freqProvinceConcours.rename(columns={'chercheur': 'count'})
freqProvinceConcours = freqProvinceConcours.merge(province_info, on='Province')


### Revoir à partir d'ici
for c in freqProvinceConcours['concours'].unique():
    subdf = freqProvinceConcours[freqProvinceConcours['concours'] == c]

    with open(f'figures/geo/canada/{c}.html', 'w') as f:
        f.write(generate_geo_figure_provinces(subdf).to_html(full_html=False, include_plotlyjs='cdn'))

    figsProvinces.append(
        {
            'Nom': c,
            'Fichier': f'figures/geo/canada/{c}.html'
        }
    ) 

    subdf = subdf[['Province', 'count']].sort_values(by='count', ascending=False)
    
    # Create the table to display aside from the figure
    tableF = subdf.rename(columns = mappingTables)

    tableF = tableF.sort_values(by=['N'], ascending=[False])
    tablesFreqProvinces[f"figures/geo/canada/{c}.html"] = tableF.to_html(classes = tableClasses, justify='left', index=False)

    # Figures - Par projet
    freqProvinceProjets = affiliationsCanada.groupby(['projet', 'concours', 'Province'])['chercheur'].count().reset_index()
    freqProvinceProjets = freqProvinceProjets.merge(province_info, on='Province')
    freqProvinceProjets = freqProvinceProjets[freqProvinceProjets['concours'] == c]
    freqProvinceProjets = freqProvinceProjets.rename(columns={'chercheur': 'count'})

    for p in freqProvinceProjets['projet'].unique():
        slugifiedName = slugify(p)[:30]

        ssubdf = freqProvinceProjets[freqProvinceProjets['projet'] == p]

        with open(f'figures/geo/canada/{slugifiedName}.html', 'w') as f:
            f.write(generate_geo_figure_provinces(ssubdf).to_html(full_html=False, include_plotlyjs='cdn'))

        figsProvinces.append(
            {
                'Nom': f"{c} -- {p}",
                'Fichier': f'figures/geo/canada/{slugifiedName}.html'
            }
        ) 

        ssubdf = ssubdf[['Province', 'count']].sort_values(by='count', ascending=False)
        
        # Create the table to display aside from the figure
        tableF = ssubdf.rename(columns = mappingTables)

        tableF = tableF.sort_values(by=['N'], ascending=[False])
        tablesFreqProvinces[f"figures/geo/canada/{slugifiedName}.html"] = tableF.to_html(classes = tableClasses, justify='left', index=False)

tablesFreqProvinces = str(tablesFreqProvinces)

### Expertises de recherche
expertises = pd.read_excel('data/fnrf_transformation_expertises.xlsx', sheet_name=0)
tout = expertises.groupby(["Champ d'expertise"])['Titre de la demande'].count().reset_index()
tout['Concours / Award'] = 'Tout'

expertises = expertises.groupby(['Concours / Award', "Champ d'expertise"])['Titre de la demande'].count().reset_index()
expertises = pd.concat([tout, expertises])
expertises = expertises.rename(columns={"Titre de la demande": "N"})
expertises = expertises[['Concours / Award', "Champ d'expertise", "N"]]


repartitionExpertisesFig = {}
repartitionExpertisesTables = {}
for concours in expertises['Concours / Award'].unique():
    df = expertises[expertises['Concours / Award'] == concours]
    fig = px.pie(
        df,
        names = "Champ d'expertise",
        color = "Champ d'expertise",
        values = 'N',
        hover_name = "Champ d'expertise",
        hole = 0.5,
        color_discrete_map=
            {
                'Santé':'#8f7db1',
                'Sciences naturelles / génie':'#6cbab9',
                'Sciences humaines et sociales':'#d47d71'
            },
        category_orders={"Champ d'expertise": ["Santé", "Sciences naturelles / génie", "Sciences humaines et sociales"]}
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(yanchor="top",y=1,xanchor="left", x=-0.5)
    )
    
    fileName = f"figures/expertises/{concours}.html"
    with open(fileName, "w", encoding="utf-8") as f:
        f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))

    table = df[["Champ d'expertise", "N"]].sort_values(by="N", ascending=False)
    table = table.to_html(classes = tableClasses, justify='left', index=False)

    repartitionExpertisesFig[str(concours)] = fileName
    repartitionExpertisesTables[str(concours)] = table


# ### Expertises - mots-clés (profils Google Scholar)
# from sentence_transformers import SentenceTransformer, util
# import time

# expertises_motCles = pd.read_csv('data/fnfr_expertises_tout.csv')

# # Model for computing sentence embeddings. We use one trained for similar questions detection
# corpus_sentences = expertises_motCles['interests'].tolist()
# model = SentenceTransformer('all-MiniLM-L6-v2')
# corpus_embeddings = model.encode(corpus_sentences, batch_size=64, show_progress_bar=True, convert_to_tensor=True)


# print("Start clustering")
# start_time = time.time()

# #Two parameters to tune:
# #min_cluster_size: Only consider cluster that have at least 25 elements
# #threshold: Consider sentence pairs with a cosine-similarity larger than threshold as similar
# clusters = util.community_detection(corpus_embeddings, min_community_size=5, threshold=0.75)

# #Print for all clusters the top 3 and bottom 3 elements
# # store the data
# cluster_name_list = []
# corpus_sentences_list = []


# for i, cluster in enumerate(clusters):
#     for sentence_id in cluster:
#         corpus_sentences_list.append(corpus_sentences[sentence_id])
#         cluster_name_list.append("{}".format(corpus_sentences[cluster[0]]))

# df_motsCles = pd.DataFrame(None)
# df_motsCles['cluster'] = cluster_name_list
# df_motsCles["mot-clé"] = corpus_sentences_list

# #Print for all clusters the top 3 and bottom 3 elements
# # store the data
# cluster_name_list = []
# corpus_sentences_list = []


# for i, cluster in enumerate(clusters):
#     for sentence_id in cluster:
#         corpus_sentences_list.append(corpus_sentences[sentence_id])
#         cluster_name_list.append("{}".format(corpus_sentences[cluster[0]]))

# df_motsCles = pd.DataFrame(None)
# df_motsCles['cluster'] = cluster_name_list
# df_motsCles["mot-clé"] = corpus_sentences_list
# table_motsCles = df_motsCles.to_html(classes = tableClasses, justify='left', index=False)


# #Print for all clusters the top 3 and bottom 3 elements
# # store the data
# cluster_name_list = []
# corpus_sentences_list = []


# for i, cluster in enumerate(clusters):
#     for sentence_id in cluster:
#         corpus_sentences_list.append(corpus_sentences[sentence_id])
#         cluster_name_list.append("{}".format(corpus_sentences[cluster[0]]))

# df_motsCles = pd.DataFrame(None)
# df_motsCles['cluster'] = cluster_name_list
# df_motsCles["mot-clé"] = corpus_sentences_list

# df = pd.DataFrame(None)
# df['cluster'] = cluster_name_list
# df["mot-clé"] = corpus_sentences_list

# from sklearn.manifold import TSNE
# import numpy as np 
# import plotly_express as px

# sentences = df['mot-clé'].tolist()
# X = np.array(model.encode(sentences))

# X_embedded = TSNE(n_components=2).fit_transform(X)

# df_embeddings = pd.DataFrame(X_embedded)
# df_embeddings = df_embeddings.rename(columns={0:'x',1:'y'})
# df_embeddings = df_embeddings.assign(cluster=df['cluster'].values)
# df_embeddings = df_embeddings.assign(mot_cle=df['mot-clé'].values)


# fig_motsCles = px.scatter(
#     df_embeddings, 
#     x='x', 
#     y='y', 
#     color='cluster', 
#     labels={'color': 'label'},
#     hover_data=['mot_cle']
# )

# with open('figures/visualization_motsCles.html', 'w') as f:
#     f.write(fig_motsCles.to_html(full_html=False, include_plotlyjs='cdn'))


### Types d'affiliations
typesAffiliations = pd.read_csv('data/fnfr_types_affiliations.csv').rename(columns={'concours':'Concours / Award'})

tout = pd.DataFrame(typesAffiliations['type affiliation'].value_counts()).reset_index()
tout['Concours / Award'] = 'Tout'

freqTypeAffiliations = typesAffiliations.groupby(['Concours / Award'])['type affiliation'].value_counts().reset_index()
freqTypeAffiliations = pd.concat([tout, freqTypeAffiliations])
freqTypeAffiliations = freqTypeAffiliations.rename(columns={"count": "N", 'type affiliation': "Affiliation"})
freqTypeAffiliations = freqTypeAffiliations[['Concours / Award', "Affiliation", "N"]]


repartitionAffiliationsFig = {}
repartitionAffiliations = {}
for concours in freqTypeAffiliations['Concours / Award'].unique():
    df = freqTypeAffiliations[freqTypeAffiliations['Concours / Award'] == concours]
    fig = px.pie(
        df,
        names = "Affiliation",
        color = "Affiliation",
        hover_name = 'Affiliation',
        color_discrete_sequence=px.colors.qualitative.Prism,
        values = 'N',
        hole = 0.5,
    )

    fig.update_layout(
        margin=dict(l=55, r=0, t=0, b=0),
        legend=dict(yanchor="top",y=1,xanchor="left", x=-0.7)
    )
    
    fileName = f"figures/affiliations/{concours}.html"
    with open(fileName, "w", encoding="utf-8") as f:
        f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))

    table = df[["Affiliation", "N"]].sort_values(by="N", ascending=False)
    table = table.to_html(classes = tableClasses, justify='left', index=False)

    repartitionAffiliationsFig[str(concours)] = fileName
    repartitionAffiliations[str(concours)] = table


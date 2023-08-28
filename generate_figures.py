import pandas as pd
import plotly
import plotly_express as px
from slugify import slugify

# charger le mapping des pays qui sera utilisé pour construire la figure
mappingPays = pd.read_csv('utils/mapping_pays_iso.csv', sep=';', encoding='UTF-8').to_dict('records')
mappingPays = {x['Pays'] : x['Alpha-3 code'] for x in mappingPays}

# Charger les données
data = pd.read_csv('data/affiliationsChercheurs.csv', sep=';')
data = data[data['Pays'] != '-']
data['Code Alpha-3 Pays'] = data['Pays'].map(mappingPays)

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
tableClasses = ['table', 'table-hover']
mappingTables = {'count': 'N'}

# Figure - Tous les projets 
# Tableau de fréquence 
freqPays = pd.DataFrame(data['Pays'].value_counts()).reset_index()
freqPays['Code Alpha-3 Pays'] = freqPays['Pays'].map(mappingPays)
freqPays = freqPays[['Pays', 'Code Alpha-3 Pays', 'count']]

with open('figures/all.html', 'w') as f:
    f.write(generate_geo_figure(freqPays).to_html(full_html=False, include_plotlyjs='cdn'))

figs.append(
    {
        'Nom': 'Tout',
        'Fichier': 'figures/all.html'
    }
)

# Create the table to display aside from the figure
tableF = freqPays.rename(columns = mappingTables)
tableF = tableF.sort_values(by=['N'], ascending=[False])[['Pays', 'N']]
tablesFreq[f"figures/all.html"] = tableF.to_html(classes = tableClasses, justify='left', index=False)

# Figures - Par concours
freqPaysConcours = data.groupby(['concours', 'Pays', 'Code Alpha-3 Pays'])['chercheur'].count().reset_index()
freqPaysConcours = freqPaysConcours.rename(columns={'chercheur': 'count'})

for c in freqPaysConcours['concours'].unique():
    subdf = freqPaysConcours[freqPaysConcours['concours'] == c]

    with open(f'figures/{c}.html', 'w') as f:
        f.write(generate_geo_figure(subdf).to_html(full_html=False, include_plotlyjs='cdn'))

    figs.append(
        {
            'Nom': c,
            'Fichier': f'figures/{c}.html'
        }
    ) 

    subdf = subdf[['Pays', 'count']].sort_values(by='count', ascending=False)
    
    # Create the table to display aside from the figure
    tableF = subdf.rename(columns = mappingTables)

    tableF = tableF.sort_values(by=['N'], ascending=[False])
    tablesFreq[f"figures/{c}.html"] = tableF.to_html(classes = tableClasses, justify='left', index=False)

    # Figures - Par projet
    freqPaysProjets = data.groupby(['projet', 'concours', 'Pays', 'Code Alpha-3 Pays'])['chercheur'].count().reset_index()
    freqPaysProjets = freqPaysProjets[freqPaysProjets['concours'] == c]
    freqPaysProjets = freqPaysProjets.rename(columns={'chercheur': 'count'})

    for p in freqPaysProjets['projet'].unique():
        slugifiedName = slugify(p)[:30]

        ssubdf = freqPaysProjets[freqPaysProjets['projet'] == p]

        with open(f'figures/{slugifiedName}.html', 'w') as f:
            f.write(generate_geo_figure(ssubdf).to_html(full_html=False, include_plotlyjs='cdn'))

        figs.append(
            {
                'Nom': f"{c} -- {p}",
                'Fichier': f'figures/{slugifiedName}.html'
            }
        ) 

        ssubdf = ssubdf[['Pays', 'count']].sort_values(by='count', ascending=False)
        
        # Create the table to display aside from the figure
        tableF = ssubdf.rename(columns = mappingTables)

        tableF = tableF.sort_values(by=['N'], ascending=[False])
        tablesFreq[f"figures/{slugifiedName}.html"] = tableF.to_html(classes = tableClasses, justify='left', index=False)

tablesFreq = str(tablesFreq)

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
# charger le mapping des pays qui sera utilisé pour construire la figure
mappingPays = pd.read_csv('utils/mapping_pays_iso.csv', sep=';', encoding='UTF-8').to_dict('records')
mappingPays = {x['Pays'] : x['Alpha-3 code'] for x in mappingPays}

# Charger les données
affiliations = pd.read_csv('data/affiliationsChercheurs.csv', sep=';')
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

with open('figures/geo/all.html', 'w') as f:
    f.write(generate_geo_figure(freqPays).to_html(full_html=False, include_plotlyjs='cdn'))

figs.append(
    {
        'Nom': 'Tout',
        'Fichier': 'figures/geo/all.html'
    }
)

# Create the table to display aside from the figure
tableF = freqPays.rename(columns = mappingTables)
tableF = tableF.sort_values(by=['N'], ascending=[False])[['Pays', 'N']]
tablesFreq[f"figures/geo/all.html"] = tableF.to_html(classes = tableClasses, justify='left', index=False)

# Figures - Par concours
freqPaysConcours = affiliations.groupby(['concours', 'Pays', 'Code Alpha-3 Pays'])['chercheur'].count().reset_index()
freqPaysConcours = freqPaysConcours.rename(columns={'chercheur': 'count'})

for c in freqPaysConcours['concours'].unique():
    subdf = freqPaysConcours[freqPaysConcours['concours'] == c]

    with open(f'figures/geo/{c}.html', 'w') as f:
        f.write(generate_geo_figure(subdf).to_html(full_html=False, include_plotlyjs='cdn'))

    figs.append(
        {
            'Nom': c,
            'Fichier': f'figures/geo/{c}.html'
        }
    ) 

    subdf = subdf[['Pays', 'count']].sort_values(by='count', ascending=False)
    
    # Create the table to display aside from the figure
    tableF = subdf.rename(columns = mappingTables)

    tableF = tableF.sort_values(by=['N'], ascending=[False])
    tablesFreq[f"figures/geo/{c}.html"] = tableF.to_html(classes = tableClasses, justify='left', index=False)

    # Figures - Par projet
    freqPaysProjets = affiliations.groupby(['projet', 'concours', 'Pays', 'Code Alpha-3 Pays'])['chercheur'].count().reset_index()
    freqPaysProjets = freqPaysProjets[freqPaysProjets['concours'] == c]
    freqPaysProjets = freqPaysProjets.rename(columns={'chercheur': 'count'})

    for p in freqPaysProjets['projet'].unique():
        slugifiedName = slugify(p)[:30]

        ssubdf = freqPaysProjets[freqPaysProjets['projet'] == p]

        with open(f'figures/geo/{slugifiedName}.html', 'w') as f:
            f.write(generate_geo_figure(ssubdf).to_html(full_html=False, include_plotlyjs='cdn'))

        figs.append(
            {
                'Nom': f"{c} -- {p}",
                'Fichier': f'figures/geo/{slugifiedName}.html'
            }
        ) 

        ssubdf = ssubdf[['Pays', 'count']].sort_values(by='count', ascending=False)
        
        # Create the table to display aside from the figure
        tableF = ssubdf.rename(columns = mappingTables)

        tableF = tableF.sort_values(by=['N'], ascending=[False])
        tablesFreq[f"figures/geo/{slugifiedName}.html"] = tableF.to_html(classes = tableClasses, justify='left', index=False)

tablesFreq = str(tablesFreq)

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
        hole = 0.5,
        color_discrete_map=
            {
                'Santé':'#636efa',
                'Sciences naturelles / génie':'#ef553b',
                'Sciences humaines et sociales':'#00cc96'
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



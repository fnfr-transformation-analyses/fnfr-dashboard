import pandas as pd

def groupOtherValues(df: pd.DataFrame, threshold: int = 6) -> pd.DataFrame:
    """
    Cette fonction prend en paramètre un objet DataFrame contenant une distirbution de fréquences et un nombre entier 
    représentant le nombre de valeurs à représenter dans un graphique. Elle retourne le DataFrame modifié en regroupant toutes 
    les autres valeurs dans une catégorie "Autre", permettant ainsi d'alléger la visualisaiton en réduisant le nombre de 
    catégories qui seornt affichées dans une visualisation.

    Par défaut, la fonction prend les 6 principales valeurs et groupe les autres dans la catégorie "Autre".
    
    À noter que la colonne contenant les fréquences associées aux catégories doit s'appeler 'count'.
    """
    top_values = df.head(threshold)
    other_values_count = df[threshold:]['count'].sum()
    col = df.columns[0]
    other_values = pd.DataFrame({col: ['Autre'], 'count': [other_values_count]})
    
    return pd.concat([top_values, other_values])


def renameLongLabels(text):
    """ 
    Cette fonction prends en paramètre une chaîne de texte et en retourne une version écourtée, ceci pour améliorer
    l'affichage de certaines figures dans le tableau de bord dans le cas où les libellés des catégories sont trop longs
    """
    if len(text) > 30:
        return (str(text)[:30] + "...")
    else: return text
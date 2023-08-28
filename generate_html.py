from generate_figures import *

tableClasses = ['table', 'table-hover']

with open('./html/header.html', encoding='utf-8') as f:
    header = f.read()


with open('./html/footer.html') as f:
    footer = f.read()

### Générer la page d'accueil 
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(header)

    ## Ajouter contenu
    f.write("<h2>FNFR Transformation - Analyse de données</h2></div>")
    f.write(f""" 
        <div class="grid" 
            style="padding-bottom:30px; width:100%; height:800px; margin-top:40px;">
            <h3>Répartition des chercheurs</h3>
            <p style="margin-left:20px;">[En construction]<br/></p>
            
            <h4>Répartition géographique</h4>
        """)
    
    # Conteneur principal
    f.write('<div style="clear: both;"></div>')
    f.write('<select style="width: 500px;" id="fileSelector" onchange="changeIframeSource()">')
    f.write('<option value="figures/all.html">Sélectionner un critère</option><p>&nbps;</p>')

    iFrames = ""
    for fig in figs:
        nom = fig['Nom']
        fichier = fig['Fichier']
        iFrames += ("\n")
        iFrames += (f'<option value="{fichier}">{nom}</option>')

    iFrames += f"""
        </select>
        <div style="clear: both;"></div>
        <!-- Conteneur gauche -->
        <div id="dataTable" class="col-md-4" 
            style="float:left; margin-top:20px; max-height:525px; overflow-y:auto;">
        </div>
        <script>
            var data = {tablesFreq};
            function changeIframeSource() {{
                var selectedFile = document.getElementById("fileSelector").value;
                document.getElementById("embeddedFrame").src = selectedFile;
            
                var selectedData = data[selectedFile];
                document.getElementById("dataTable").innerHTML = selectedData;
                document.getElementById("dataTable").style.height = "600px"
            }}
        </script>


        <!-- Conteneur droit -->
        <div id="container" class="col-md-8" style="float: right; margin-top:10px; padding-bottom:20px;">
            <iframe id="embeddedFrame" height="525" width="100%" 
                style="padding:0px; overflow-y:auto;">
            </iframe>
        </div>
    """
    f.write(iFrames)
    f.write('<div style="clear: both; margin-top:500px;"><hr/></div>')
            
    f.write("""
        <h3>Expertises de recherche</h3>
        <h3>Publications</h3>
    </div>
    """)

    f.write(footer)
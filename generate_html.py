from generate_figures import *

tableClasses = ['table', 'table-hover']

with open('./html/header.html', encoding='utf-8') as f:
    header = f.read()


with open('./html/footer.html') as f:
    footer = f.read()

### Générer la page d'accueil 
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(header)

    f.write("<h2>FNFR Transformation - Analyse de données</h2></div>")
    f.write('<div class="accordion" id="accordionExample">')
    f.write(f""" 
        <div class="grid" 
            style="padding-bottom:30px; width:100%; height:1200px; margin-top:40px;">
            <h3 id="chercheurs">Répartition des chercheurs</h3>
    """)

    ids = ['collapseOne', 'collapseTwo', 'collapseThree', 'collapseFour']
    i = 0

    for indicateur in repartitionChercheurs.keys():
        id = ids[i]

        f.write(
        f"""
        <div class="accordion-item">
            <h2 class="accordion-header">
                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#{id}" aria-expanded="false" aria-controls="{id}">
                    {indicateur}
                </button>
            </h2>
            <div id="{id}" class="accordion-collapse collapse" data-bs-parent="#accordionExample">
                <div class="accordion-body" style="height:350px;">
                    <!-- Conteneur gauche -->
                    <div class="col-md-4" style="float:left; margin-top:20px; max-height:525px; overflow-y:auto;">
                        {repartitionChercheurs[indicateur]['table']}
                    </div>
                    <!-- Conteneur droit -->
                    <div class="col-md-8" style="float:left; margin-top:10px; padding-left:80px; padding-right: 0px; padding-bottom:20px;">
                        {repartitionChercheurs[indicateur]['fig']}
                    </div>  
                </div>
            </div>            
        </div>

        """
        )
        i+=1

    # Répartition géographique -- International
    f.write('<h4 style = "margin-top: 50px; margin-bottom:12px;">Répartition géographique</h4>')
    f.write("""
        <nav>
        <div class="nav nav-tabs" id="nav-tab" role="tablist">
            <button class="nav-link active" id="nav-home-tab" data-bs-toggle="tab" data-bs-target="#international" type="button" role="tab" aria-controls="nav-home" aria-selected="true">International</button>
            <button class="nav-link" id="nav-profile-tab" data-bs-toggle="tab" data-bs-target="#canada" type="button" role="tab" aria-controls="nav-profile" aria-selected="false">Canada</button>
        </div>
        </nav>
        <div class="tab-content" id="nav-tabContent">
    """)
    
    # Conteneur principal
    f.write('<div class="tab-pane fade show active" id="international" role="tabpanel" aria-labelledby="nav-home-tab" tabindex="0">')
    f.write('<div style="clear: both; margin-top:30px;"></div>')
    f.write('<select class="form-select" style="width:40%; margin-bottom:20px;" id="fileSelector" onchange="changeIframeSource()">')
    f.write('<option value="figures/geo/international/all.html">Sélectionner un critère</option>')

    iFrames = ""
    for fig in figs:
        nom = fig['Nom']
        fichier = fig['Fichier']
        selected = "selected" if fichier == "figures/geo/international/all.html" else ""
        iFrames += ("\n")
        iFrames += (f'<option value="{fichier}" {selected}>{nom}</option>')

    iFrames += f"""
        </select>
        <div style="clear: both;"></div>
        <!-- Conteneur gauche -->
        <div id="dataTable" class="col-md-4" 
            style="float:left; margin-top:20px; max-height:525px; overflow-y:auto;">
        </div>
        <!-- Conteneur droit -->
        <div id="container" class="col-md-8" style="float: right; margin-top:0px; padding-bottom:20px;">
            <iframe id="embeddedFrame" height="525" width="100%" 
                style="padding:0px; overflow-y:auto;">
            </iframe>
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
    """
    f.write(iFrames)
    f.write("""
        <script>
            // Appel initial pour afficher l'iFrame par défaut
            changeIframeSource();
        </script> 
    """)
    f.write('<div style="clear:both; margin-top:600px;"><hr style="margin-bottom: 30px;"/></div>') 
    f.write('</div>')

    # Répartition géographique -- Canada 
    f.write('<div class="tab-pane fade" id="canada" role="tabpanel" aria-labelledby="nav-profile-tab" tabindex="0">')
    # Conteneur principal
    f.write('<div style="clear: both; margin-top:30px;"></div>')
    f.write('<select class="form-select" style="width:40%; margin-bottom:20px;" id="fileSelectorProvince" onchange="changeIframeSourceProvince()">')
    f.write('<option value="figures/geo/canada/all.html">Sélectionner un critère</option>')

    iFrames = ""
    for fig in figsProvinces:
        nom = fig['Nom']
        fichier = fig['Fichier']
        selected = "selected" if fichier == "figures/geo/canada/all.html" else ""
        iFrames += ("\n")
        iFrames += (f'<option value="{fichier}" {selected}>{nom}</option>')

    iFrames += f"""
        </select>
        <div style="clear: both;"></div>
        <!-- Conteneur gauche -->
        <div id="dataTableProvince" class="col-md-4" 
            style="float:left; margin-top:20px; max-height:525px; overflow-y:auto;">
        </div>
        <!-- Conteneur droit -->
        <div id="containerProvince" class="col-md-8" style="float: right; padding-left:40px; margin-top:20px;">
            <iframe id="embeddedFrameProvince" height="525" width="100%"
                style="padding:0px; overflow-y:auto;">
            </iframe>
        </div>
        <script>
            var dataProvince = {tablesFreqProvinces};
            function changeIframeSourceProvince() {{
                var selectedFileProvince = document.getElementById("fileSelectorProvince").value;
                document.getElementById("embeddedFrameProvince").src = selectedFileProvince;
            
                var selectedDataProvince = dataProvince[selectedFileProvince];
                document.getElementById("dataTableProvince").innerHTML = selectedDataProvince;
                document.getElementById("dataTableProvince").style.height = "600px"
            }}
        </script>
    """
    f.write(iFrames)
    f.write("""
        <script>
            // Appel initial pour afficher l'iFrame par défaut
            changeIframeSourceProvince();
        </script> 
    """)
    f.write('<div style="clear:both; margin-top:600px;"><hr style="margin-bottom: 30px;"/></div>') 
    f.write("</div>")


    ### Expertises de recherche
    concours = expertises['Concours / Award'].unique().tolist()
    f.write("""
        <h3 id="expertises">Expertises de recherche</h3>
    """)

    f.write('<select class="form-select" style="width:40%; margin-bottom:20px;" id="AwardSelector" onchange="changeAwardExpertise()">')
    f.write(f'<option value="{concours[0]}" select>{concours[0]}</option>')

    for x in concours[1:]:
        f.write(f'<option value="{x}">{x}</option>')

    f.write(
        f"""
        </select>
        <div style="clear: both;"></div>
        <!-- Conteneur gauche -->
        <div id="tableExpertises" class="col-md-4" 
            style="float:left; margin-top:20px; max-height:525px; overflow-y:auto;">
        </div>
        <!-- Conteneur droit -->
        <div class="col-md-8" style="float: right; margin-top:10px; padding-bottom:20px;">
            <iframe id="figureExpertise" height="525" width="100%" 
                style="padding-left:40px; padding-right:40px; height:350px;">
            </iFrame>
        </div>
        <script>
            function changeAwardExpertise() {{
                var tables = {repartitionExpertisesTables}
                var figures = {repartitionExpertisesFig}
                var selectedAward = document.getElementById("AwardSelector").value;

                document.getElementById("tableExpertises").innerHTML = tables[selectedAward];

                document.getElementById("figureExpertise").src = figures[selectedAward];
            }}
        </script>

        """
    )
    f.write("""
        <script>
            // Appel initial pour afficher l'iFrame par défaut
            changeAwardExpertise();
        </script> 
    """)

    # # Mots-clés
    # f.write('<div style="clear:both; margin-top:400px;"><hr style="margin-bottom: 30px;"/></div>') 
    # f.write("""
    #     <h4><b>Expertises</b> (mots-clés)</h3>
    # """)


    # f.write(
    #     f"""
    #     </select>
    #     <div style="clear: both;"></div>
    #     <!-- Conteneur gauche -->
    #     <!-- Conteneur gauche -->
    #     <div id="tableExpertises" class="col-md-4" 
    #         style="float:left; margin-top:20px; max-height:350px; overflow-y:auto;">
    #         {table_motsCles}
    #     </div>
    #     <!-- Conteneur droit -->
    #     <div class="col-md-8" style="float: right; margin-top:10px; padding-bottom:20px;">
    #         <iframe src='figures/visualization_motsCles.html' height="525" width="100%" 
    #             style="padding-left:40px; padding-right:40px; height:350px;">
    #          </iframe>
    #     </div>
    #     """
    # )

    ### Affiliations 
    f.write('<div style="clear:both; margin-top:400px;"><hr style="margin-bottom: 30px;"/></div>') 

    concours = freqTypeAffiliations['Concours / Award'].unique().tolist()
    f.write("""
        <h3 id="affiliations">Affiliations</h3>
    """)

    f.write('<select class="form-select" style="width:40%; margin-bottom:20px;" id="AwardSelectorAff" onchange="changeAwardAffiliation()">')
    f.write(f'<option value="{concours[0]}" select>{concours[0]}</option>')

    for x in concours[1:]:
        f.write(f'<option value="{x}">{x}</option>')

    f.write(
        f"""
        </select>
        <div style="clear: both;"></div>
        <!-- Conteneur gauche -->
        <div id="tableAffiliation" class="col-md-4" 
            style="float:left; margin-top:0px; max-height:525px; overflow-y:auto;">
        </div>
        <!-- Conteneur droit -->
        <div class="col-md-8" style="float: right; margin-top:10px; padding-bottom:20px;">
            <iframe id="figureAffiliation" height="525" width="100%" 
                style="padding-left:40px; padding-right:0px; height:375px;">
            </iFrame>
        </div>
        <script>
            function changeAwardAffiliation() {{
                var tablesAff = {repartitionAffiliations}
                var figuresAff = {repartitionAffiliationsFig}
                var selectedAwardAff = document.getElementById("AwardSelectorAff").value;

                document.getElementById("tableAffiliation").innerHTML = tablesAff[selectedAwardAff];

                document.getElementById("figureAffiliation").src = figuresAff[selectedAwardAff];
            }}
        </script>

        """
    )
    f.write("""
        <script>
            // Appel initial pour afficher l'iFrame par défaut
            changeAwardAffiliation();
        </script> 
    """)
    

    f.write(footer)
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import pdf2image
import re
#import PIL

def ocr_core_pdf(image, thresh):
    text = ""
    # PHASE 1 : CONVERSION
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
    #img = pdf2image.convert_from_path(filename, grayscale=True, poppler_path = r"C:\Mes Programmes\poppler-0.90.0_x86\bin")
    #for cur_img in img:
        #PHASE 2 : NOIR & BLANC
    fn = lambda x : 255 if x > thresh else 0
    cur_img = image.convert('L').point(fn, mode='1')
#        r.save('foo.png')
#        cur_img = cur_img.convert("1")
#        cur_img.save("output.png")
        #PHASE 3 : EXTRACTION DE TEXTE
    text += pytesseract.image_to_string(cur_img, config='--oem 1 -c tessedit_char_whitelist=-()0123456789CHAMPEX')
    return text

def ocr_core_img(image):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
    text = pytesseract.image_to_string(Image.open(filename), config='--oem 1 -c tessedit_char_whitelist=-()0123456789CHAMPEX')
    return text

#print(ocr_core_pdf('scan043.pdf'))
#print(ocr_core_img('image.png'))

strict = False
doc = "scan053.pdf"

results = [{},{},{},{},{},{},{}]
thresh = 90
error = 0

print("Analyse du fichier " + doc + (" en mode Strict" if strict == True else " en mode Non Strict"))

image = pdf2image.convert_from_path(doc, grayscale=True, poppler_path = r"C:\Mes Programmes\poppler-0.90.0_x86\bin")[0]

while thresh < 250:
    #PHASES 1, 2, 3
    text = ocr_core_pdf(image, thresh)
    text = re.sub("\n", "", text)
    #PHASE 4 : ANALYSE
    if strict:
        code = re.search("[\[\(][\[|\(]([\w\s=~\-\(\/]*)[\)\]][\)\]]", text, re.I)
    else:
        code = re.search("[\[|\(]?[\[|\(]([\w\s\(€]*[=~\-\(]+[\w\s\(€]*[=~\-\(]+[\w\s\(€]*[=~\-\(]+[\w\s\(€=~\-\(\/]*)[\)\]][\)\]]?", text, re.I)
    if code:
        #PHASE 5 : NETTOYAGE
        code = code.group(1)
        code = re.sub("€", "C", code)
        code = re.sub("[_=~]", "-", code)
        code = re.sub("\(", "C", code)
        code = re.sub("\s", "", code)
        code = re.sub("o|O", "0", code)
        code = re.sub("a|A", "4", code)
        code = code.upper()
        clusters = code.split("-")
        cur_id = 0
        #PHASE 6 : INDEXATION
        for cur_cluster in clusters:
            if cur_cluster != "":
                if cur_cluster in results[cur_id]:
                    results[cur_id][cur_cluster] += 1
                else:
                    results[cur_id][cur_cluster] = 1
                cur_id += 1
        thresh += 1
        error = 0
        print(thresh, code)
    else:
        print(thresh, "Aucun résultat", text)
        error += 1
        thresh += 1
        if error >= 3:
            error = 0
            thresh += 9

sorted_results = []
#PHASE 8 : TRIAGE
for cluster in results:
    sorted_results.append(sorted(cluster, key=cluster.get, reverse=True))

print(sorted_results)

#PHASE 9: TRAITEMENT
#CLUSTER 1 - DOCUMENT RELATIF A
max_confidence_level = 2
possibilities = {"Non trouvé" : -1}
for cur_value in sorted_results[0]:
    if re.search("^[CD]$", cur_value):
        confidence_level = 2
        final_value = cur_value
    elif re.search("[CD]", cur_value):
        confidence_level = 1
        reg_value = re.search("([CD])", cur_value).group(1)
        final_value = reg_value
    else:
        confidence_level = 0
        final_value = None
    if final_value == "C":
        doc_related = "Cours"
    elif final_value == "D":
        doc_related = "Divers"
    else:
        doc_related = "Inconnu"
    if doc_related in possibilities.keys():
        if confidence_level > possibilities[doc_related]:
            possibilities[doc_related] = confidence_level
    else:
        possibilities[doc_related] = confidence_level
sorted_possibilities = sorted(possibilities, key=possibilities.get, reverse=True)
print("Document relatif à : "+sorted_possibilities[0]+ "  Indice de confiance : "+ str(possibilities[sorted_possibilities[0]])+"/"+str(max_confidence_level))

#CLUSTER 2 - ANNEE/CLASSE DU DOCUMENT
max_confidence_level = 4
possibilities = {"Non trouvé" : -1}
for cur_value in sorted_results[1]:
    if re.search("CP\d", cur_value):
        confidence_level = 4
        final_value = re.search("CP(\d)", cur_value).group(1)
    elif re.search("[CP]\d", cur_value):
        confidence_level = 3
        final_value = re.search("[CP](\d)", cur_value).group(1)
    elif re.search("^\d$", cur_value):
        confidence_level = 2
        final_value = re.search("^(\d)$", cur_value).group(1)
    elif re.search("\d", cur_value):
        confidence_level = 1
        final_value = re.search("(\d)", cur_value).group(1)
    else:
        confidence_level = 0
        final_value = None
    if final_value == "1":
        doc_classe = "Année 1"
    elif final_value == "2":
        doc_classe = "Année 2"
    else:
        doc_classe = "Inconnu"
    possibilities[doc_classe] = confidence_level
sorted_possibilities = sorted(possibilities, key=possibilities.get, reverse=True)
print("Année/Classe du document : "+sorted_possibilities[0]+ "  Indice de confiance : "+ str(possibilities[sorted_possibilities[0]])+"/"+str(max_confidence_level))


#CLUSTER 3 - MATIERE DU DOCUMENT
max_confidence_level = 4
final_value = None
possibilities = {"Non trouvé" : -1}
available_matieres_all = {"FR" : "Français", "MT" : "Maths", "PH" : "Physique"}
or_condition_all = "|".join(available_matieres_all.keys())
for cur_value in sorted_results[2]:
    if re.search(or_condition_all, cur_value):
        confidence_level = 4
        final_value = available_matieres_all[re.search("("+or_condition_all+")", cur_value).group(1)]
    else:
        for cur_mat in available_matieres_all.keys():
            if re.search("(?:"+cur_mat[0]+")"+".*"+"(?:"+cur_mat[1]+")", cur_value):
                confidence_level = 3
                final_value = available_matieres_all[cur_mat]
                break
    if not final_value:
        for cur_mat in available_matieres_all.keys():
            if re.search("^(?:"+cur_mat[0]+")|(?:"+cur_mat[1]+")$", cur_value):
                confidence_level = 2
                final_value = available_matieres_all[cur_mat]
                break
    if not final_value:
        for cur_mat in available_matieres_all.keys():
            if re.search("["+cur_mat+"]", cur_value):
                confidence_level = 1
                final_value = available_matieres_all[cur_mat]
                break
    if not final_value:
        confidence_level = 0
        final_value = None
    if final_value:
        doc_matiere = final_value
    else:
        doc_matiere = "Inconnue"
    possibilities[doc_matiere] = confidence_level
sorted_possibilities = sorted(possibilities, key=possibilities.get, reverse=True)
print("Matière du document : "+sorted_possibilities[0]+ "  Indice de confiance : "+ str(possibilities[sorted_possibilities[0]])+"/"+str(max_confidence_level))


#CLUSTER 4 - CHAPITRE DU DOCUMENT
max_confidence_level = 4
possibilities = {"Non trouvé" : -1}
for cur_value in sorted_results[3]:
    if re.search("CH\d+", cur_value):
        confidence_level = 4
        final_value = re.search("CH(\d+)", cur_value).group(1)
    elif re.search("[CH]\d+", cur_value):
        confidence_level = 3
        final_value = re.search("[CH](\d+)", cur_value).group(1)
    elif re.search("^\d+$", cur_value):
        confidence_level = 2
        final_value = re.search("^(\d+)$", cur_value).group(1)
    elif re.search("\d+", cur_value):
        confidence_level = 1
        final_value = re.search("(\d+)", cur_value).group(1)
    else:
        confidence_level = 0
        final_value = None
    if final_value:
        doc_chapitre = "Chapitre "+final_value
    else:
        doc_chapitre = "Inconnu"
    possibilities[doc_chapitre] = confidence_level
sorted_possibilities = sorted(possibilities, key=possibilities.get, reverse=True)
print("Chapitre du document : "+sorted_possibilities[0]+ "  Indice de confiance : "+ str(possibilities[sorted_possibilities[0]])+"/"+str(max_confidence_level))


#CLUSTER 5 - TYPE DE COURS, NUMERO, ET TYPE DU DOCUMENT
max_confidence_level = 4
final_value_cours_type = None
final_value_doc_type = None
final_value_doc_number = None
possibilities = {"Non trouvé|Non trouvé|Non trouvé" : -1}
available_cours_type = {"CU" : "Cours", "EX" : "Exercice", "TP" : "Travaux pratiques", "TD" : "Travaux Dirigés", "DS": "Devoir surveillé"}
available_doc_type = {"E" : "Ennoncé", "B" : "Brouillon", "R" : "Réponse", "C" : "Corrigé"}
or_condition_cours_type = "|".join(available_cours_type.keys())
for cur_value in sorted_results[4]:
    if re.search("(?:"+or_condition_cours_type+")\d+["+"".join(available_doc_type.keys())+"]", cur_value):
        confidence_level = 4
        final_value_cours_type = available_cours_type[re.search("("+or_condition_cours_type+")\d+["+"".join(available_doc_type.keys())+"]", cur_value).group(1)]
        final_value_doc_type = available_doc_type[re.search("(?:"+or_condition_cours_type+")\d+(["+"".join(available_doc_type.keys())+"])", cur_value).group(1)]
        final_value_doc_number = re.search("(?:"+or_condition_cours_type+")(\d+)["+"".join(available_doc_type.keys())+"]", cur_value).group(1)
    if not final_value_cours_type:
        for cur_cours in available_cours_type.keys():
            if re.search(cur_cours[0]+".*"+cur_cours[1]+".*\d+.*["+"".join(available_doc_type.keys())+"]", cur_value):
                confidence_level = 3
                final_value_cours_type = available_cours_type[cur_cours]
                final_value_doc_type = available_doc_type[re.search(cur_cours[0]+".*"+cur_cours[1]+".*\d+.*(["+"".join(available_doc_type.keys())+"])", cur_value).group(1)]
                final_value_doc_number = re.search(cur_cours[0]+".*"+cur_cours[1]+".*(\d+).*(["+"".join(available_doc_type.keys())+"])", cur_value).group(1)
                break
    if not final_value_cours_type:
        for cur_cours in available_cours_type.keys():
            if re.search("^["+cur_cours+"].*\d+.*["+"".join(available_doc_type.keys())+"]", cur_value):
                confidence_level = 2
                final_value_cours_type = available_cours_type[cur_cours]
                final_value_doc_type = available_doc_type[re.search("^["+cur_cours+"].*\d+.*(["+"".join(available_doc_type.keys())+"])", cur_value).group(1)]
                final_value_doc_number = re.search("^["+cur_cours+"].*(\d+).*["+"".join(available_doc_type.keys())+"]", cur_value).group(1)
                break
    if not final_value_cours_type:
        for cur_cours in available_cours_type.keys():
            if re.search("["+cur_cours+"].*\d+.*["+"".join(available_doc_type.keys())+"]?", cur_value):
                confidence_level = 1
                final_value_cours_type = available_cours_type[cur_cours]
                output = re.search("["+cur_cours+"].*\d+.*(["+"".join(available_doc_type.keys())+"]?)", cur_value).group(1)
                if output:
                    final_value_doc_type = available_doc_type[output]
                else:
                    final_value_doc_type = None
                final_value_doc_number = re.search("["+cur_cours+"].*(\d+).*["+"".join(available_doc_type.keys())+"]?", cur_value).group(1)
                break
    if not final_value_cours_type:
        confidence_level = 0
        final_value_cours_type = None
        final_value_doc_type = None
        final_value_doc_number = None
    if final_value_cours_type:
        doc_cours_type = final_value_cours_type
        doc_number = final_value_doc_number
        if final_value_doc_type:
            doc_type = final_value_doc_type
        else:
            doc_type = "Inconnu"
    else:
        doc_cours_type = "Inconnu"
        doc_number = "Inconnu"
        doc_type = "Inconnu"
    possibilities[doc_cours_type+"|"+doc_number+"|"+doc_type] = confidence_level
sorted_possibilities = sorted(possibilities, key=possibilities.get, reverse=True)
values = sorted_possibilities[0].split("|")
print("Type de cours : "+values[0]+ "  Indice de confiance : "+ str(possibilities[sorted_possibilities[0]])+"/"+str(max_confidence_level))
print("Numéro de document : "+values[1]+ "  Indice de confiance : "+ str(possibilities[sorted_possibilities[0]])+"/"+str(max_confidence_level))
print("Type de document : "+values[2]+ "  Indice de confiance : "+ str(possibilities[sorted_possibilities[0]])+"/"+str(max_confidence_level))


#AUTRES CLUSTERS (6+) - NUMERO DE PAGE ET DATE
max_confidence_level = 4
for cluster_number in range(5,len(sorted_results)):
    final_value_type = None
    final_value_value = None
    possibilities = {"Non trouvé|Non trouvé" : -1}
    for cur_value in sorted_results[cluster_number]:
        if re.search("P\d+", cur_value):
            confidence_level = 4
            final_value_type = "Page"
            final_value_value = re.search("P(\d+)", cur_value).group(1)
        elif re.search("D(?:0[1-9]|[12][0-9]|3[01])[- /.](?:0[1-9]|1[012])(?:[- /.](?:20)?\d\d)?", cur_value):
            confidence_level = 4
            final_value_type = "Date"
            date_result = re.search("D(0[1-9]|[12][0-9]|3[01])[- /.](0[1-9]|1[012])(?:[- /.](?:20)?(\d\d))?", cur_value)
            try:
                final_value_value = date_result.group(1)+"|"+date_result.group(2)+"|"+date_result.group(3)
            except:
                final_value_value = date_result.group(1)+"|"+date_result.group(2)
        elif re.search("P.*\d+", cur_value):
            confidence_level = 3
            final_value_type = "Page"
            final_value_value = re.search("P.*(\d+)", cur_value).group(1)
        elif re.search("D.*\d+.*[- /.].*\d+(?:.*[- /.].*(?:20)?\d+)?", cur_value):
            confidence_level = 3
            final_value_type = "Date"
            date_result = re.search("D.*(\d+).*[- /.].*(\d+)(?:.*[- /.].*(?:20)?(\d+))?", cur_value)
            try:
                final_value_value = date_result.group(1)+"|"+date_result.group(2)+"|"+date_result.group(3)
            except:
                final_value_value = date_result.group(1)+"|"+date_result.group(2)
        elif re.search("^\d+$", cur_value):
            confidence_level = 2
            final_value_type = "Page"
            final_value_value = re.search("^(\d+)$", cur_value).group(1)
        elif re.search("^\d+.*[- /.].*\d+(?:.*[- /.].*(?:20)?\d+)?$", cur_value):
            confidence_level = 2
            final_value_type = "Date"
            date_result = re.search("^(\d+).*[- /.].*(\d+)(?:.*[- /.].*(?:20)?(\d+))?$", cur_value)
            try:
                final_value_value = date_result.group(1)+"|"+date_result.group(2)+"|"+date_result.group(3)
            except:
                final_value_value = date_result.group(1)+"|"+date_result.group(2)
        elif re.search("\d+", cur_value):
            confidence_level = 1
            final_value_type = "Page"
            final_value_value = re.search("(\d+)", cur_value).group(1)
        elif re.search("\d+.*\d+(?:.*(?:20)?\d+)?", cur_value):
            confidence_level = 1
            final_value_type = "Date"
            date_result = re.search("(\d+).*(\d+)(?:.*(?:20)?(\d+))?", cur_value)
            try:
                final_value_value = date_result.group(1)+"|"+date_result.group(2)+"|"+date_result.group(3)
            except:
                final_value_value = date_result.group(1)+"|"+date_result.group(2)
        else:
            confidence_level = 0
            final_value_type = None
            final_value_value = None
        possibilities[str(final_value_type)+"|"+str(final_value_value)] = confidence_level
    sorted_possibilities = sorted(possibilities, key=possibilities.get, reverse=True)
    values = sorted_possibilities[0].split("|")
    if values[0] == "None":
        print("Cluster inconnu (Echec de reconnaissance)  Indice de confiance : "+ str(possibilities[sorted_possibilities[0]])+"/"+str(max_confidence_level))
    elif values[0] == "Non trouvé":
        print("Cluster inexistant  Indice de confiance : "+ str(possibilities[sorted_possibilities[0]])+"/"+str(max_confidence_level))
    else:
        print(values[0]+ " du document : "+values[1]+ "  Indice de confiance : "+ str(possibilities[sorted_possibilities[0]])+"/"+str(max_confidence_level))

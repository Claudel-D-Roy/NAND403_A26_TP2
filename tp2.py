import time
import json
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QCheckBox, QHBoxLayout
from maya import cmds


class OutlinerOrganiser(QWidget):
    #-----------------------------------------------------------------------
    def __init__(self): #Constructeur
        super().__init__() #Super = constructeur du parent
        self.setWindowTitle("Outliner Organiser")
        self.create_ui()
    #-----------------------------------------------------------------------

    #-----------------------------------------------------------------------
    def json_file(self, file_json): #Fonction pour le json
        try: 
            file = open(file_json)
            data = json.load(file) 
        except (json.JSONDecodeError, FileNotFoundError):
            cmds.warning(f"Impossible de charger le JSON : {file_json}")

        else:
            file.close()
            return data      
    #-----------------------------------------------------------------------    

    #-----------------------------------------------------------------------
    #Ouvre le ui et set les objects a leur place, appel la fonction on_click a la fin avec le bouton
    def create_ui(self):
        #Layout
        layout_v = QVBoxLayout(self)

        #label
        label_json = QLabel("entre JSON rule path")

        #checked box
        self.apply_section_only = QCheckBox("Apply on selection only")
        self.apply_colors = QCheckBox("Apply colors")
        self.apply_reorder = QCheckBox("Apply reorder")

        #Place pour le text json
        self.text_json = QLineEdit()

        #bouton
        button = QPushButton("Organise Outliner")

        #place les trucs dans le layout
        layout_v.addWidget(label_json)
        layout_v.addWidget(self.text_json)
        layout_v.addWidget(self.apply_section_only)
        layout_v.addWidget(self.apply_colors)
        layout_v.addWidget(self.apply_reorder)
        layout_v.addWidget(button)
        
        button.clicked.connect(lambda : self.on_click())
    #-----------------------------------------------------------------------
     
    #-----------------------------------------------------------------------
    def on_click(self):  
        
        data = self.json_file(self.text_json.text()) #Appel le json
        
        if data is None: return # return si data est vide

        cmds.undoInfo(openChunk=True, chunkName="OutlinerOrganiser") # fonction pour le ctrl.Z

        #Met le résultat en bool dans un variable pour savoir si c'est checked ou non
        selection_only = self.apply_section_only.isChecked()
        colors = self.apply_colors.isChecked()
        reorder = self.apply_reorder.isChecked()
        
        try:
            if selection_only:
                objects = cmds.ls(selection = True, long = True) #Selection active
            else : 
                objects = cmds.ls(dag=True, long= True, transforms = True) #Tous les éléments du outliner
        
            if colors:
                self.apply_colors_to(objects, data) # appel la fonction qui va appliquer les couleurs
      
            if reorder:
                self.apply_reorder_to(objects, data) # appel la fonction qui va order les choses
        finally: 
            cmds.undoInfo(closeChunk=True) # fin du ctrl.Z
    #-----------------------------------------------------------------------

    #-----------------------------------------------------------------------
    def apply_colors_to(self, objects, data): 
        t0 = time.perf_counter() #Debug, compte le temps que la fonction prends.
        try:
            for obj in objects: #loop dans les objets a modifier
                split_name = obj.split("|")[-1] # split l'objet pour avoir juste la key
                for key, color in data.items(): # loop dans les items du date en avec key et color
                    if split_name.startswith(key): # si l'objet spliter comment avec la key on fait les changements
                        cmds.setAttr(obj + ".useOutlinerColor", True) #Met a true le changement de couleur dans maya
                        cmds.setAttr(obj + ".outlinerColor", *color, type="double3") # change l'obj avec la couleur approprié
                        break
        finally:
            print("on_click total :", round(time.perf_counter() - t0, 3), "s", flush=True) # print le temps de mon debug
    #-----------------------------------------------------------------------

    #-----------------------------------------------------------------------
    def matches_rule(self, obj, data): #trie les objets que j'ai besoin seulement, on ne veut pas les camera ou autre
        short_name = obj.split("|")[-1] #split le nom pour avoir juste la key
        return any(short_name.startswith(key) for key in data) # return juste les objets a modifier
    #-----------------------------------------------------------------------

    #-----------------------------------------------------------------------
    def apply_reorder_to(self, objects, data) : #order les objets
       to_sort = [o for o in objects if self.matches_rule(o, data)] # garde seulement les object du json
       to_sort.sort(key=lambda o: o.split("|")[-1].lower()) #tri croissant sur le nom spliter

       for obj in reversed(to_sort): #place chaque obj en ordre en partant du dernier
        cmds.reorder(obj, front=True) # au final le premier du tri finit en haut
    #-----------------------------------------------------------------------           
                    
def main():
    global widget
    try:
        widget.close()
    except Exception:
        pass
    widget = OutlinerOrganiser()
    widget.resize(300, 100)
    widget.show()
 
main()
   
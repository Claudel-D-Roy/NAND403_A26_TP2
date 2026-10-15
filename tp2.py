import time
import json
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QCheckBox, QHBoxLayout
from maya import cmds


class OutlinerOrganiser(QWidget):
    def __init__(self): #Constructeur
        super().__init__() #Super = constructeur du parent
        self.setWindowTitle("Outliner Organiser")
        self.create_ui()

    def json_file(self, file_json):
        try: 
            file = open(file_json)
            data = json.load(file) 
        except json.JSONDecodeError:
            print(f'Could not load data from {file_json}')

        except FileNotFoundError:
            print(f'Could not load data from {file_json}')
        else:
            file.close()
            return data      

    def create_ui(self):
        layout_v = QVBoxLayout(self)
        label_json = QLabel("entre JSON rule path")
      
        self.apply_section_only = QCheckBox("Apply on selection only")
        self.apply_colors = QCheckBox("Apply colors")
        self.apply_reorder = QCheckBox("Apply reorder")
        self.text_json = QLineEdit()
        
        button = QPushButton("Organise Outliner")

        layout_v.addWidget(label_json)
        layout_v.addWidget(self.text_json)
        layout_v.addWidget(self.apply_section_only)
        layout_v.addWidget(self.apply_colors)
        layout_v.addWidget(self.apply_reorder)
        layout_v.addWidget(button)
        
        button.clicked.connect(lambda : self.on_click())

     
     
    def on_click(self):  
        
        data = self.json_file(self.text_json.text())
        if data is None: return
        cmds.undoInfo(openChunk=True, chunkName="OutlinerOrganiser")
        selection_only = self.apply_section_only.isChecked()
        colors = self.apply_colors.isChecked()
        reorder = self.apply_reorder.isChecked()
        try:
            if selection_only:
                objects = cmds.ls(selection = True, long = True) #Selection active
            else : 
                objects = cmds.ls(dag=True, long= True, transforms = True) #Tous les éléments du outliner
        
            if colors:
                self.apply_colors_to(objects, data)
      
            if reorder:
                self.apply_reorder_to(objects, data)
        finally: 
            cmds.undoInfo(closeChunk=True)


    def apply_colors_to(self, objects, data):
        t0 = time.perf_counter()
        try:
            for obj in objects:
                split_name = obj.split("|")[-1]
                for key, color in data.items():
                    if split_name.startswith(key):
                        cmds.setAttr(obj + ".useOutlinerColor", True)
                        cmds.setAttr(obj + ".outlinerColor", *color, type="double3")
                        break
        finally:
            print("on_click total :", round(time.perf_counter() - t0, 3), "s", flush=True)


    def matches_rule(self, obj, data):
        short_name = obj.split("|")[-1]
        return any(short_name.startswith(key) for key in data)
    
    def apply_reorder_to(self, objects, data) :
       to_sort = [o for o in objects if self.matches_rule(o, data)]
       to_sort.sort(key=lambda o: o.split("|")[-1].lower())

       for obj in reversed(to_sort):
        cmds.reorder(obj, front=True)
               
                    
       
         

        

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
   
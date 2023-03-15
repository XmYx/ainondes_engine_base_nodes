#from qtpy.QtWidgets import QLineEdit, QLabel, QPushButton, QFileDialog, QVBoxLayout
from qtpy import QtWidgets

from ainodes_frontend.base import register_node, get_next_opcode
from ainodes_frontend.base import AiNode, CalcGraphicsNode
from ainodes_frontend.node_engine.node_content_widget import QDMNodeContentWidget
from ainodes_frontend.node_engine.utils import dumpException

OP_NODE_EXEC_SPLITTER = get_next_opcode()

class ExecSplitterWidget(QDMNodeContentWidget):
    def initUI(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(15,15,15,25)
        self.setLayout(layout)



@register_node(OP_NODE_EXEC_SPLITTER)
class ExecSplitterNode(AiNode):
    icon = "icons/in.png"
    op_code = OP_NODE_EXEC_SPLITTER
    op_title = "Execute Splitter"
    content_label_objname = "exec_splitter_node"
    category = "exec"

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1,1])
        #self.content.button.clicked.connect(self.evalImplementation)
        self.busy = False
        # Create a worker object
    def initInnerClasses(self):
        self.content = ExecSplitterWidget(self)
        self.grNode = CalcGraphicsNode(self)
        self.grNode.height = 160
        self.grNode.width = 256
        self.content.setMinimumWidth(256)
        self.content.setMinimumHeight(160)
        self.input_socket_name = ["EXEC"]
        self.output_socket_name = ["EXEC_1", "EXEC_2"]


    def evalImplementation(self, index=0):
        self.markDirty(True)
        self.markInvalid(True)
        self.busy = False
        if len(self.getOutputs(1)) > 0:
            self.executeChild(1)
            #thread1 = threading.Thread(target=self.getOutputs(1)[0].eval)
            #thread1.start()
            #thread1.join()
        if len(self.getOutputs(0)) > 0:
            self.executeChild(0)
            #thread0 = threading.Thread(target=self.getOutputs(0)[0].eval)
            #thread0.start()
            #thread0.join()
        return None

    def onMarkedDirty(self):
        self.value = None











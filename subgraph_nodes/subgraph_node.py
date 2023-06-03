import threading
import time

from qtpy import QtCore
from qtpy import QtWidgets
from ainodes_frontend.base import register_node, get_next_opcode
from ainodes_frontend.base import AiNode, CalcGraphicsNode
from ainodes_frontend.node_engine.node_content_widget import QDMNodeContentWidget

OP_NODE_SUBGRAPH = get_next_opcode()
OP_NODE_SUBGRAPH_INPUT = get_next_opcode()
OP_NODE_SUBGRAPH_OUTPUT = get_next_opcode()

class SubgraphNodeWidget(QDMNodeContentWidget):
    done_signal = QtCore.Signal()
    def initUI(self):
        #self.graph_json = {}
        pass

    def serialize(self) -> dict:
        res = {}
        #res['graph_json'] = self.graph_json
        return res



    def deserialize(self, data, hashmap={}, restore_id:bool=True) -> bool:
        #self.graph_json = data['graph_json']
        return True


@register_node(OP_NODE_SUBGRAPH)
class SubgraphNode(AiNode):
    icon = "ainodes_frontend/icons/base_nodes/exec.png"
    op_code = OP_NODE_SUBGRAPH
    op_title = "Subgraph"
    content_label_objname = "subgraph_node"
    category = "Subgraph Nodes"
    help_text = "Execution Node\n\n" \
                "Execution chain is essential\n" \
                "in aiNodes. You control the flow\n" \
                "You control the magic. Each value\n" \
                "is created and stored at execution\n" \
                "once a node is validated, you don't\n" \
                "have to run it again in order to get\n" \
                "it's value, just simply connect the\n" \
                "relevant data line. Only execute, if you\n" \
                "want, or have to get a new value."
    load_graph = True

    def __init__(self, scene, graph_json=None):
        super().__init__(scene, inputs=[2,3,5,6,1], outputs=[2,3,5,6,1])
        self.graph_json = graph_json


    def initInnerClasses(self):
        #self.graph_json = {}
        self.content = SubgraphNodeWidget(self)
        self.grNode = CalcGraphicsNode(self)
        self.grNode.icon = self.icon
        self.grNode.height = 220
        self.grNode.width = 220
        self.content.eval_signal.connect(self.evalImplementation)
        self.graph_window = None
        self.name = f"{self.getID(0)}_Subgraph"

        """if not self.load_graph:
            print("Empty Subgraph Node")
        else:
            print(self.graph_json)
            self.scene.getView().parent().window().json_open_signal.emit(self)
            self.graph_window.widget().scene.deserialize(self.graph_json["nodes"])
            self.graph_window.widget().filename = f"{self.getID(0)}_Subgraph"
            print("INIT COMPLETE", self.graph_json)"""

    def evalImplementation_thread(self, index=0, *args, **kwargs):

        nodes = self.graph_window.widget().scene.nodes
        for node in nodes:
            if isinstance(node, SubGraphOutputNode):
                #self.graph_window.widget().scene.traversing = True
                node.true_parent = self
                break
        for node in nodes:
            if isinstance(node, SubGraphInputNode):

                node.data = self.getInputData(3)
                node.images = self.getInputData(2)
                node.latents = self.getInputData(0)
                node.conds = self.getInputData(1)

                node.content.eval_signal.emit()
                break

        #while self.graph_window.widget().scene.traversing:
            #time.sleep(0.1)
            #timer = QtCore.QTimer()
            #timer.setSingleShot(True)
            #timer.setInterval(5)
            #timer.start()
        #print(self.graph_json)

        #print(self.graph_window.widget().scene.nodes)
        #print(self.graph_window.widget().scene.serialize())


        #data = self.getInputData(3)
        #images = self.getInputData(2)
        #latents = self.getInputData(0)
        #conds = self.getInputData(1)

        """for node in nodes:
            if isinstance(node, SubGraphOutputNode):
                self.graph_window.widget().scene.traversing = True
                node.content.eval_signal.emit()
                data = node.getOutput(3)
                images = node.getOutput(2)
                latents = node.getOutput(0)
                conds = node.getOutput(1)
                print(images)"""

        return None

    @QtCore.Slot(object)
    def onWorkerFinished(self, result):
        super().onWorkerFinished(None)
        #print("SUBGRAPH DONE SKIPPING EXECUTION")
        if result:
            #print("SUBGRAPH DONE EXECUTING NEXT NODE IF ANY")
            self.setOutput(0, result[0])
            self.setOutput(1, result[1])
            self.setOutput(2, result[2])
            self.setOutput(3, result[3])
            self.executeChild(4)

    def onDoubleClicked(self, event=None):
        if self.graph_window:
            for window in self.scene.getView().parent().window().mdiArea.subWindowList():
                if window == self.graph_window:
                    self.scene.getView().parent().window().mdiArea.setActiveSubWindow(window)
        else:
            if self.graph_json:
                self.scene.getView().parent().window().json_open_signal.emit(self)
            else:

                self.scene.getView().parent().window().file_new_signal.emit(self)
                self.graph_window.widget().filename = f"{self.getID(0)}_Subgraph"

    def serialize(self):
        """
        Serialize the node's data into a dictionary.

        Returns:
            dict: The serialized data of the node.
        """
        if self.graph_window:
            self.graph_json = self.graph_window.widget().scene.serialize()

        res = super().serialize()
        res['op_code'] = self.__class__.op_code
        res['content_label_objname'] = self.__class__.content_label_objname
        if self.graph_window:
            res['node_graph'] = self.graph_window.widget().scene.serialize()
        return res

    def deserialize(self, data, hashmap={}, restore_id=True):
        """
        Deserialize the node's data from a dictionary.

        Args:
            data (dict): The serialized data of the node.
            hashmap (dict): A dictionary of node IDs and their corresponding objects.
            restore_id (bool): Whether to restore the original node ID. Defaults to True.

        Returns:
            bool: True if deserialization is successful, False otherwise.
        """
        #print(data)
        if 'node_graph' in data:
            self.graph_json = data['node_graph']
            if self.load_graph:
                self.scene.getView().parent().window().json_open_signal.emit(self)
                self.load_graph = None
        res = super().deserialize(data, hashmap, restore_id)
        return res


@register_node(OP_NODE_SUBGRAPH_INPUT)
class SubGraphInputNode(AiNode):
    icon = "ainodes_frontend/icons/base_nodes/exec.png"
    op_code = OP_NODE_SUBGRAPH_INPUT
    op_title = "Subgraph Inputs"
    content_label_objname = "subgraph_input_node"
    category = "Subgraph Nodes"
    help_text = "Execution Node\n\n" \
                "Execution chain is essential\n" \
                "in aiNodes. You control the flow\n" \
                "You control the magic. Each value\n" \
                "is created and stored at execution\n" \
                "once a node is validated, you don't\n" \
                "have to run it again in order to get\n" \
                "it's value, just simply connect the\n" \
                "relevant data line. Only execute, if you\n" \
                "want, or have to get a new value."

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[2, 3, 5, 6, 1])

    def initInnerClasses(self):
        self.content = SubgraphNodeWidget(self)
        self.grNode = CalcGraphicsNode(self)
        self.grNode.icon = self.icon
        self.grNode.height = 180
        #self.grNode.width = 800
        #self.content.setMinimumWidth(600)
        #self.content.setMinimumHeight(400)
        self.content.eval_signal.connect(self.evalImplementation)
        self.latents = None
        self.conds = None
        self.images = None
        self.data = None

    def run(self, data, images, latens, conds):
        pass


    def evalImplementation_thread(self, index=0, *args, **kwargs):

        self.setOutput(0, self.latents)
        self.setOutput(1, self.conds)
        self.setOutput(2, self.images)
        self.setOutput(3, self.data)
        #print("REACHED SUBGRAPH INPUT NODE")
        return True

    @QtCore.Slot(object)
    def onWorkerFinished(self, result):
        #print("REACHED SUBGRAPH INPUT NODE END")
        super().onWorkerFinished(None)
        self.executeChild(4)


@register_node(OP_NODE_SUBGRAPH_OUTPUT)
class SubGraphOutputNode(AiNode):
    icon = "ainodes_frontend/icons/base_nodes/exec.png"
    op_code = OP_NODE_SUBGRAPH_OUTPUT
    op_title = "Subgraph Outputs"
    content_label_objname = "subgraph_output_node"
    category = "Subgraph Nodes"
    help_text = "Execution Node\n\n" \
                "Execution chain is essential\n" \
                "in aiNodes. You control the flow\n" \
                "You control the magic. Each value\n" \
                "is created and stored at execution\n" \
                "once a node is validated, you don't\n" \
                "have to run it again in order to get\n" \
                "it's value, just simply connect the\n" \
                "relevant data line. Only execute, if you\n" \
                "want, or have to get a new value."

    def __init__(self, scene):
        super().__init__(scene, inputs=[2, 3, 5, 6, 1], outputs=[])

    def initInnerClasses(self):
        self.content = SubgraphNodeWidget(self)
        self.grNode = CalcGraphicsNode(self)
        self.grNode.icon = self.icon
        self.grNode.height = 180
        #self.grNode.width = 800
        #self.content.setMinimumWidth(600)
        #self.content.setMinimumHeight(400)
        self.content.eval_signal.connect(self.evalImplementation)
        self.true_parent = None

    def run(self, data, images, latens, conds):
        pass


    def evalImplementation_thread(self, index=0, *args, **kwargs):
        #print("REACHED SUBGRAPH OUTPUT NODE")

        latents = self.getInputData(0)
        conds = self.getInputData(1)
        images = self.getInputData(2)
        data = self.getInputData(3)

        return[latents, conds, images, data]


    @QtCore.Slot(object)
    def onWorkerFinished(self, result):
        #print("REACHED SUBGRAPH OUTPUT NODE END")
        super().onWorkerFinished(None)

        self.setOutput(0, result[0])
        self.setOutput(1, result[1])
        self.setOutput(2, result[2])
        self.setOutput(3, result[3])
        #self.scene.traversing = None

        #print(self.true_parent.onWorkerFinished(result))
        if self.true_parent:
            self.true_parent.onWorkerFinished(result)
        #self.content.done_signal.emit()









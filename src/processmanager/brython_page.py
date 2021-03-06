from browser import alert, document as doc
from browser import websocket
from browser.html import BR, DIV, H2, H3,H4, CODE, LI,A
import json
import functools


def on_open(evt):
    # Re-setup our button:
    btn = doc['btn_connect']
    btn.text = "Connected"
    btn.classList.remove('btn-warning')
    btn.classList.add('btn-success')

    btn.bind('click', btnClkDisonnect)



def on_close(evt):
    btn = doc['btn_connect']
    btn.text = "Connect.."
    btn.classList.remove('btn-success')
    btn.classList.add('btn-warning')

    btn.bind('click', btnClkConnect)


def on_message(evt):
    print("Message recv'ed")
    div = doc['outputwindow']
    code= doc['outputcode']
    code <= BR() + evt.data
    div.scrollTop = div.scrollHeight;

    handle_msg(evt.data)

def btnClkConnect(evt):
    evt.stopPropagation()
    _open(evt)

def btnClkDisonnect(evt):
    evt.stopPropagation()
    ws.close()

ws = None
def _open(ev):
    if not __BRYTHON__.has_websocket:
        alert("WebSocket is not supported by your browser")
        return
    global ws

    # open a web socket
    ws = websocket.WebSocket("ws://localhost:8765")

    ws.bind('open',on_open)
    ws.bind('message',on_message)
    ws.bind('close',on_close)
    ws.bind('error',on_error)

def on_error(evt):
    global ws
    if ws is not None:
        ws.close()

def close_socket(evt):
    evt.stopPropagation()
    global ws
    if ws is not None:
        ws.close()







def handle_msg(data):
    print("Handling msg:")
    msgs = json.loads(data)
    print(msgs)
    for msg in msgs:
        msg_type=msg['msg-type']
        print(msg_type)

        if msg_type=='cfg-process-mgr-list':
            handle_msg_config_process_mgr_list(msg)

        elif msg_type == 'cfg-process-mgr-details':
            handle_msg_cfg_process_mgr_details(msg)

        elif msg_type=='output':
            handle_msg_output(msg)

        elif msg_type=='cfg-process-mgr-closed':
            handle_msg_process_mgr_closed(msg)

        else:
            print ("Unexpected messgae: %s", msg_type)










# ------- Choosing a new process manager: --------------


def switch_to_new_process_mgr(evt, id_):
    global ws
    print("Switching to new Manager: %d" % id_)
    doc["procmgrdropbox"].text = "...(loading)..."

    # Fire and forget the message -- we'll get the response back that will
    # ultimately cause a GUI update:
    msgs = json.dumps([{'msg-type':'set-process-mgr','process-mgr-id':id_}])
    ws.send(msgs)


def handle_msg_config_process_mgr_list(msg):
    """Enable the dropdown, clear out the old contents, and update"""
    dropListNode = doc['procmgrlist']

    dropListNode.clear()
    doc["procmgrdropbox"].classList.remove('disabled')

    print("MsgConfigProcessMgrList")
    for process_mgr in msg['process_mgrs']:
        print(process_mgr)
        newNode = A(process_mgr['name'])
        id_ = process_mgr['id']
        #newNode.bind('click', lambda evt :switch_to_new_process_mgr(evt=evt,id_=id_) )
        newNode.bind('click', functools.partial(switch_to_new_process_mgr, id_=id_)  )
        dropListNode <= LI(newNode)

    # And switch to the first node by default:
    switch_to_new_process_mgr(None, id_=msg['process_mgrs'][0]['id'])


# ------- Switching to a new process manager: --------------

def handle_msg_cfg_process_mgr_details(msg):
    global code_blks

    print("Setting process mgr")
    print(msg)
    process_mgr_name = msg['name']
    doc["procmgrdropbox"].text = process_mgr_name

    # Clear out the old contents from process_container:
    ctn = doc['ctn_process']
    code_blks = {}
    ctn.clear()

    for process in msg['processes']:
        process_name = process['name']
        process_id = process['id']

        heading = DIV("[%s] %s (%d)"%(process_mgr_name, process_name, process_id), Class="panel-heading")
        contents = ""#H2(process_name)
        new_div = DIV(heading + DIV(contents, Class="panel-body"), Class="panel panel-default" )
        ctn <= new_div

        for output_pipe in process['outpipes'].values():
            print ("output_pipe",output_pipe)
            nCode = CODE("XX",id="jlk")
            container = DIV( DIV( nCode,style={'overflow':'scroll','height':'150px'}),
                        Class='container')
            new_div <= H3(output_pipe, )
            new_div <= container
            code_blks[ (process_id, output_pipe) ] = nCode





# ------- Switching to a new process manager: --------------
def handle_msg_process_mgr_closed(msg):
    """<div class="alert alert-danger" role="alert">...</div>"""
    ctn = doc['ctn_alerts']
    # TODO - Fix the dismiss button:
    #<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>
    new_div = DIV("Process manager closed", Class="alert alert-danger alert-dismissible", role="alert" )
    ctn <= new_div


# Map (process_id, pipe_name) => code-html node
code_blks = {}

def handle_msg_output(msg):
    global code_blks

    proc_id = msg['process_id']
    pipe_name = msg['pipe']

    codeBlock = code_blks.get((proc_id,pipe_name),None)
    if codeBlock:
        codeBlock <= BR() + msg['contents']
        codeBlock.parentNode.scrollTop = codeBlock.parentNode.scrollHeight;


doc['btn_connect'].bind('click', btnClkConnect)


import datetime
import json
import os

from tabulate import tabulate

from UIFunc import RunScriptClass, to_abs_path


def getScriptsInfo(script_list):
    info = []
    headers = ['ScriptName', 'Length', 'Extension']
    for script_path in script_list:
        events, module, label_dict = RunScriptClass.parsescript(script_path)
        time = sum([e.delay for e in events])
        info.append([script_path, str(time) + 'ms', module if module else 'None'])
    return tabulate(info, headers=headers)


def new_script_path():
    now = datetime.datetime.now()
    script = '%s.txt' % now.strftime('%m%d_%H%M%S')
    path = os.path.join(to_abs_path('scripts'), script)
    return path


class ScriptClipper:
    def __init__(self):
        self.record = []
        self.extension = []

    def recordMethod(self):
        output = json.dumps(self.record, indent=1, ensure_ascii=False)
        output = output.replace('\r\n', '\n').replace('\r', '\n')
        output = output.replace('\n   ', '').replace('\n  ', '')
        output = output.replace('\n ]', ']')
        with open(new_script_path(), 'w', encoding='utf-8') as f:
            f.write(output)

    def concatScripts(self, script_list):
        self.record = []
        modules = []
        for script_path in script_list:
            unit_events, unit_module_name, unit_label_dict = RunScriptClass.parsescript(script_path)
            modules.append(unit_module_name)
            self.record += unit_events
        if len(list(set(modules))) != 1:
            raise Exception('Chosen Scripts of Different Modules')
        self.record = [[e.delay, e.event_type, e.message, e.action] for e in self.record]
        self.recordMethod()

    def sliceScript(self, script_path, start_time, stop_time):
        self.record = []
        events, self.extension, label_dict = RunScriptClass.parsescript(script_path)
        time = 0
        for e in events:
            operate_time = time + e.delay
            if start_time <= operate_time <= stop_time:
                if time < start_time:
                    e.delay = operate_time - start_time
                self.record.append([e.delay, e.event_type, e.message, e.action])
                print('append')
            elif operate_time > stop_time:
                break
            time = operate_time
        self.recordMethod()

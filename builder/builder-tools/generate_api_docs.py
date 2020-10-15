import os
import sys
import pydoc
import logging

#from pathlib import Path

current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.realpath(os.path.join(current_dir, os.pardir, os.pardir)))

class DocsGenerator:
    def __init__(self,
                 links_raltive_path="",
                 module_header="# Module {}",
                 functions_header="## Module functions",
                 class_header="## Class {}",
                 function_header="### {}"
                 ):
        self.links_path = links_raltive_path
        self.module_header = module_header
        self.functions_header = functions_header
        self.class_header = class_header
        self.function_header = function_header

    def get_full_markdown(self, module):
        output = [self.module_header.format(module.__name__)]

        if module.__doc__:
            output.append(module.__doc__)

        output.append(self.functions_header)
        output.extend(self.get_functions(module))
        output.extend(self.get_classes(module))

        return output

    def get_classes(self, item):
        output = list()
        for cls_name, cls in pydoc.inspect.getmembers(item, pydoc.inspect.isclass):
            if cls_name.startswith("_") or cls_name == "__class__":
                continue
            if cls.__module__ != item.__name__:
                continue

            output.append(self.class_header.format(cls_name))
            output.append(pydoc.inspect.getdoc(cls) or '...')  # Get the docstring
            output.extend(self.get_functions(cls))  # Get the functions
            output.extend(self.get_classes(cls))  # Recurse into any subclasses
            output.append('\n')
        return output

    def get_functions(self, item):
        output = []
        for func_name, func in pydoc.inspect.getmembers(item, pydoc.inspect.isfunction):
            if func_name.startswith('_') and func_name != '__init__':
                continue
            # if func.__module__ != item.__name__:
            #     continue

            output.append(self.function_header.format(func_name.replace('_', '\\_')))

            output.append('```py')
            output.append(f'def {func_name}{pydoc.inspect.signature(func)}')
            output.append('```')
            # print(pydoc.inspect.getsourcelines(func[1]))

            output.append(pydoc.inspect.getdoc(func) or "")  # get the docstring

        return output

    def generate_docs(self, module_import_path, output_path):
        try:
            module = pydoc.safeimport(module_import_path)
            # print(module.__file__)

            if module is None:
                logging.error("Module not found")
                return
        except pydoc.ErrorDuringImport as e:
            logging.error(f"Error while trying to import {module_import_path}: {e}")
        else:
            docs = self.get_full_markdown(module)
            with open(output_path, 'w') as f:
                for line in docs:
                    f.write(line.replace("\n", os.linesep) + '\n')


if __name__ == '__main__':
    modules_list = [
        "lib.messaging",
    ]
    gen = DocsGenerator()
    for module in modules_list:
        gen.generate_docs(module, os.path.realpath(os.path.join("msg.md")))
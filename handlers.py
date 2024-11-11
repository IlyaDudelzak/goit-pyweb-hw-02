from fields import AddressBook, datetime, Phone
from bithday import string_to_date
from collections import defaultdict
from datetime import datetime, date, time
import pickle
import re

def checkTypes(types:list|tuple, vals:list|tuple):
    if(len(types) != len(vals)):
        return False
    for i, t in enumerate(types):
        v = vals[i]
        if(type(v) != t):
            return False
    return True

def chackTypesExc(types:list|tuple, vals:list|tuple):
    if(not checkTypes(types, vals)):
        raise TypeError

class ContactError(Exception):
    pass

class Assistant:
    example = None
    types=(int, float, str, datetime, date, time, Phone)
    def __init__(self):
        self.book = self.__load_data()
        self.handlers = defaultdict(list)
        self.mainLoopActive = False
        Assistant.example = self

    class Handler():
        handlers = defaultdict(list)  
        
        @staticmethod
        def get_sample(type_: type):
            if(type_ == int):
                return 1
            elif(type_ == float):
                return 1.3
            elif(type_ == str):
                return "Sample"
            elif(type == datetime):
                return datetime.now()
            elif(type == date):
                return datetime.now().date()
            elif(type == time):
                return datetime.now().time()
            elif(type == Phone):
                return Phone("0000000000")
            else:
                return None
            

        @classmethod
        def check_command(self, func, commands, args:tuple=()):
            regex = '^[a-z_][a-z0-9_]*'
            # args_ = [Assistant.example]
            # if(len(args) > 0):
            #     for i in args:
            #         args_.append(self.get_sample(i))
            # print(args, args_)
            # try:
            #     func(*args_)
            # except TypeError:
            #     raise SyntaxError("Command doesnt apply to its args")
            for i in commands:
                if(not re.search(regex, i)):
                    raise SyntaxError(f"Invalid command: {i}")
                if(i in self.handlers):
                    c = self.handlers.get(i)
                    for j in c:
                        if(j.args == args):
                            raise SyntaxError(f"Already defided same command with the same args: {i}({j})")

        def __init__(self, func, commands:str|tuple, args:type|tuple|list=(), unargs:int=0, argnames=None):
            if(type(args) != tuple and type(args) != list):
                args = (args,)
            self.check_command(func, commands, args)
            self.func = func
            self.commands = commands
            self.args = args
            self.unargs = unargs
            self.argnames = argnames
            for c in commands:
                self.handlers[c].append(self)
        
        def __call__(self, args):            
            _args = []
            for i, arg_ in enumerate(args):
                try:
                    arg = self.args[i]
                    if(arg == str):
                        _args.append(arg_)
                    elif(arg == int):
                        _args.append(int(arg_))
                    elif(arg == float):
                        _args.append(float(arg_))
                    elif(arg == datetime):
                        try:
                            _args.append(string_to_date(arg_))
                        except ValueError:
                            return "Invalid date format. Use DD.MM.YYYY"
                    
                except ValueError:
                    return "Wrong args!"
            try:
                return self.func(Assistant.example, *args)
            except (KeyError,IndexError,ContactError, ValueError) as e:
                return str(e)
    
    def __save_data(self, filename="addressbook.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(self.book, f)

    @staticmethod
    def __load_data(filename="addressbook.pkl"):
        try:
            with open(filename, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return AddressBook()
        
    def command_handler(self, commands:tuple|str, args:tuple|type = (), unnecessaryArgs:int = 0, argnames = None):
        if(type(commands) != tuple):
            commands = (commands,)
        if(type(args) != tuple):
            args = (args,)
        def dec(func):
            if(len(args) < unnecessaryArgs):
                raise SyntaxError("More unnecessary args than args total!")
            for i in args:
                if(i not in self.types):
                    raise SyntaxError(f"Wrong arg type: {i}")
            handler = self.Handler(func, commands, args, unnecessaryArgs, argnames)
            for i in commands:
                self.handlers[i].append(handler)
            return handler.func
        return dec
        
    def handle_input(self, input:str):
        args = 0
        cmd = ""
        try:
            cmd, *args = input.split()
            cmd = cmd.strip().lower()
        except ValueError:
            return "You haven`t entered command"
        
        handlers = self.Handler.handlers.get(cmd)
        if(handlers == None):
            return "Command not found"
        returns = []
        for handler in handlers:
            try:
                if(not(len(args) < len(handler.args) - handler.unargs and len(args) > len(handler.args))):
                    r = handler(args)
                    if(r != None):
                        returns.append(r)
                
            except ValueError:
                return "Wrong args!"
            

        return returns
    
    def mainLoop(self):
        self.mainLoopActive = True
        while self.mainLoopActive:
            try:
                res = self.handle_input(input(">>> "))
                if(type(res) == list and len(res) > 0):
                    for i in res:
                        print(i)
            except Exception as e:
                print(e)
            except KeyboardInterrupt:
                self.mainLoopActive = False
        print("\nGood bye!")
        self.__save_data()
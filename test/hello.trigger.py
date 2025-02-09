# Development Helpers #########################################################################################
# Import sbms related modules here for develepment purpose

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import model
    
# Execution Members #########################################################################################

def process_message(name: str):
    return f'Hello {name}!'

# MCR Runner #########################################################################################

@model.model_status_controller_sync
def run_(mcr: model.ModelCaseReference):
    
    name = mcr.request_json['name']
    message = process_message(name)
    
    return {
        'case-id': mcr.id,
        'message': message
    }

# Basic Members #########################################################################################

NAME = 'Hello'

CATEGORY = 'First Example'

CATEGORY_ALIAS = 'fe'
 
def PARSING(self: model.launcher, request_json: dict, other_dependent_ids: list[str]=[]):
    
    hello_mcr = self.build_model_case(request_json, other_dependent_ids)
    
    return [hello_mcr]

def RESPONSING(self: model.launcher, core_mcr: model.ModelCaseReference, default_pre_mcrs: list[model.ModelCaseReference], other_pre_mcrs: list[model.ModelCaseReference]):
    
    return core_mcr.make_response({
        'case-id': 'TEMPLATE',
        'description': 'NONE'
    })

def RUNNING(self: model.launcher, args: list[str]):
    
    v1 = args[-1]    # model case id
    
    hello_mcr = self.connect_model_case(v1)
    
    run_(hello_mcr)
    
import json 
from aws_cdk import (
    aws_lambda,
    core,
    aws_iam,
    aws_ssm as ssm,
    aws_dynamodb as ddb,

)
from project_config import (
    PYTHON_LAMBDA_CONFIG,
    BASE_ENV_VARIABLES,
    STACK_NAME
)


from utils.utils import (
    get_param
)

tabla_usuarios_ssm = get_param(f'/ct-manager/{STACK_NAME}/voice-mail-api/users-ddb-table')



class OnCall(core.Construct):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        tabla_usuarios = ddb.Table.from_table_name(self,"tabla_usr_from_ssm",table_name=tabla_usuarios_ssm)

        lambda_router = aws_lambda.Function(
            self, "lambdarouter",handler="lambda_function.lambda_handler",
            code=aws_lambda.Code.asset("./lambdas/oncall/contact_router_lambda"),
            description='[ONCALL] Obtiene el numero on call',
            **PYTHON_LAMBDA_CONFIG, 
            environment=json.loads(json.dumps(dict( TABLE_NAME=tabla_usuarios.table_name, **BASE_ENV_VARIABLES)))
        )

        DDB_POLICY = aws_iam.PolicyStatement(
            actions=["dynamodb:*"], 
            resources=[tabla_usuarios.table_arn, '{}/*'.format(tabla_usuarios.table_arn)])

        lambda_router.add_to_role_policy(DDB_POLICY)

        ssm.StringParameter(self, "contact-router", 
            description='Lambda que obtiene el numero de la persona oncall',
            parameter_name="/ct-manager/{}/oncall/contact-router-function-arn".format(STACK_NAME), 
            string_value=lambda_router.function_arn)


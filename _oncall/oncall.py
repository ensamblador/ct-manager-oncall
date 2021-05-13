import json 
from aws_cdk import (
    aws_lambda,
    core,
    aws_ssm as ssm,

)
from project_config import (
    PYTHON_LAMBDA_CONFIG,
    BASE_ENV_VARIABLES,
    STACK_NAME
)


class OnCall(core.Construct):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        lambda_router = aws_lambda.Function(
            self, "lambdarouter",handler="lambda_function.lambda_handler",
            code=aws_lambda.Code.asset("./lambdas/oncall/contact_router_lambda"),
            description='[ONCALL] Obtiene el numero on call',
            **PYTHON_LAMBDA_CONFIG, 
            environment=json.loads(json.dumps(dict( UserPhoneNumber ='+56974769647', **BASE_ENV_VARIABLES)))
        )

        ssm.StringParameter(self, "contact-router", 
            description='Lambda que obtiene el numero de la persona oncall',
            parameter_name="/ct-manager/{}/oncall/contact-router-function-arn".format(STACK_NAME), 
            string_value=lambda_router.function_arn)


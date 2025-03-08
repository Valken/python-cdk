import aws_cdk as core
import aws_cdk.assertions as assertions

from python_cdk_sam.python_cdk_sam_stack import PythonCdkSamStack

# example tests. To run these tests, uncomment this file along with the example
# resource in python_cdk_sam/python_cdk_sam_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = PythonCdkSamStack(app, "python-cdk-sam")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })

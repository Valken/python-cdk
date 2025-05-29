# from cdk.api_stack import ApiStack


# example tests. To run these tests, uncomment this file along with the example
# resource in cdk/api_stack.py
def test_sqs_queue_created():
    pass
    # app = core.App()
    # stack = ApiStack(app, "python-cdk-sam")
    # template = assertions.Template.from_stack(stack)


#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })


def test_lambda_layer_created():
    pass
    # app = App()
    # stack = ApiStack(app, "TestStack")
    # template = Template.from_stack(stack)
    #
    # # Assert that a Lambda LayerVersion resource is created
    # template.has_resource_properties("AWS::Lambda::LayerVersion", {})

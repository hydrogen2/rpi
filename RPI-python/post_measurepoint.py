from enos.message.upstream.tsl.MeasurepointPostRequest import MeasurepointPostRequest

def post_measurepoint(client, measurepoint_name, measurepoint_value):
    print("Posting", measurepoint_name)
    print()
    measurepoint = MeasurepointPostRequest.builder().add_measurepoint(measurepoint_name, measurepoint_value).build()
    client.publish(measurepoint)





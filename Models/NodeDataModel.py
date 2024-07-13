class NodeDataModel:
    def __init__(self, _id: int, description: str):
        self.id = _id
        self.section = description

    @staticmethod
    def from_response(json_response):
        return NodeDataModel(_id=json_response['Id'], description=json_response['Description'])

    @staticmethod
    def from_response_list(json_response_list):
        return [NodeDataModel.from_response(item) for item in json_response_list]

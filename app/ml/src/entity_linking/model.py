import torch.nn as nn
import timm

class EntityLinkingModel(nn.Module):
    def __init__(self, model_name, out_features, pretrained=True):
        super(EntityLinkingModel, self).__init__()
        self.model = timm.create_model(model_name, pretrained=pretrained)
        in_features = self.model.classifier.in_features
        self.model.classifier = nn.Linear(in_features, out_features)
        # self.model.classifier = nn.Identity()
        # self.model.global_pool = nn.Identity()
        # self.pooling = GeM()
        # self.embedding = nn.Linear(in_features, embedding_size)
        # self.fc = ArcMarginProduct(embedding_size, 
                                   # CONFIG["num_classes"],
                                   # s=CONFIG["s"], 
                                   # m=CONFIG["m"], 
                                   # easy_margin=CONFIG["ls_eps"], 
                                   # ls_eps=CONFIG["ls_eps"])

    def forward(self, images, labels):
        output = self.model(images)
        # features = self.model(images)
        # pooled_features = self.pooling(features).flatten(1)
        # output = self.embedding(pooled_features)
        # output = self.fc(embedding, labels)
        return output
    
    # def extract(self, images):
    #     features = self.model(images)
    #     pooled_features = self.pooling(features).flatten(1)
    #     embedding = self.embedding(pooled_features)
    #     return embedding

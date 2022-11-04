import torch.nn as nn
import timm

class EntityLinkingModel(nn.Module):
    def __init__(self, model_name, out_features, pretrained=True):
        super(EntityLinkingModel, self).__init__()
        self.model = timm.create_model(model_name, pretrained=pretrained)
        # ADD
        for param in self.model.parameters():
          param.requires_grad = False
        # until here
        in_features = self.model.classifier.in_features
        self.model.classifier = nn.Linear(in_features, out_features)

    def forward(self, images, labels):
        output = self.model(images)
        return output
    
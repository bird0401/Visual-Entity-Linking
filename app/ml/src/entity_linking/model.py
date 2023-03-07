import torch.nn as nn
import timm

import logging
import logging.config
from yaml import safe_load

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("model")


class EntityLinkingModel(nn.Module):
    def __init__(self, model_name, out_features, pretrained=True):
        assert out_features > 0
        super(EntityLinkingModel, self).__init__()
        self.model = timm.create_model(model_name, pretrained=pretrained)
        in_features = self.model.classifier.in_features
        self.model.classifier = nn.Linear(in_features, out_features)

    def forward(self, images, labels=None):
        output = self.model(images)
        return output

#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import glob
from importlib import import_module
import torch
# from mysite.Nets.Net import Net
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
import time
import logging

# BERT model construction
from torch import nn


class BertClassifier(nn.Module):
    def __init__(self, bert_model):
        super(BertClassifier, self).__init__()
        self.bert = bert_model
        self.linear1 = nn.Linear(768, 128)
        self.linear2 = nn.Linear(64, 2)
        self.activation = nn.ReLU()

    def forward(self, x, mask_attn):
        outputs = self.bert(input_ids=x, attention_mask=mask_attn)
        output = outputs[0][:, 0, :]
        res = self.linear1(output)
        res = self.activation(res)
        res = self.linear2(res)
        return res


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "easy_config_server.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

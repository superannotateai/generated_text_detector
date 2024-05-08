import torch.nn.functional as F
import torch.nn as nn
import torch


class BCEWithLogitsLossSmoothed(nn.Module):
    """BCEWithLogitsLoss with label smoothing.

    :param label_smoothing: The label smoothing factor (from 0 to 1), defaults to 0.0
    :type label_smoothing: float, optional
    :param reduction: Specifies the reduction to apply to the output, defaults to 'mean'
    :type reduction: str, optional
    """
    def __init__(self, label_smoothing=0.0, reduction='mean'):
        super(BCEWithLogitsLossSmoothed, self).__init__()
        assert 0 <= label_smoothing <= 1, "label_smoothing value must be from 0 to 1"
        self.label_smoothing = label_smoothing
        self.reduction = reduction

        self.bce_with_logits = nn.BCEWithLogitsLoss(reduction=reduction)
        self.bce = nn.BCELoss()

    def forward(self, logits: torch.Tensor, target: torch.Tensor) ->  torch.Tensor:
        """Forward pass of the loss function.

        :param input: The logits tensor
        :type input: torch.Tensor
        :param target: The target tensor
        :type target: torch.Tensor
        :return: Computed loss
        :rtype: torch.Tensor
        """
        logits, target = logits.squeeze(), target.squeeze()
        pred_probas = F.sigmoid(logits)
        entropy = self.bce(pred_probas, pred_probas)
        bce_loss = self.bce_with_logits(logits, target)
        loss = bce_loss - self.label_smoothing * entropy 

        return loss

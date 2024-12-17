from transformers import RobertaModel
from transformers.modeling_outputs import SequenceClassifierOutput
from huggingface_hub import PyTorchModelHubMixin
import torch.nn as nn
import torch

from generated_text_detector.utils.model.bce_smoothed_loss import BCEWithLogitsLossSmoothed


class RobertaClassifier(nn.Module, PyTorchModelHubMixin):
    """Roberta based text classifier.

    :param config: Configuration dictionary containing model parameters
        should contain following keys: `pretrain_checkpoint`, `classifier_dropout`, `num_labels`, `label_smoothing`
    :type config: dict
    """
    def __init__(self, config: dict):
        super().__init__()
        
        self.roberta  = RobertaModel.from_pretrained(config["pretrain_checkpoint"], add_pooling_layer = False)

        self.dropout = nn.Dropout(config["classifier_dropout"])
        self.dense = nn.Linear(self.roberta.config.hidden_size, config["num_labels"])

        self.loss_func = BCEWithLogitsLossSmoothed(config["label_smoothing"])

    def forward(
        self,
        input_ids: torch.LongTensor | None,
        attention_mask: torch.FloatTensor | None = None,
        token_type_ids: torch.LongTensor | None = None,
        position_ids: torch.LongTensor | None = None,
        head_mask: torch.FloatTensor | None = None,
        inputs_embeds: torch.FloatTensor | None = None,
        labels: torch.LongTensor | None = None,
        output_attentions: bool | None = None,
        output_hidden_states: bool | None = None,
        return_dict: bool | None = None,
        cls_output: bool | None = None,
    ):
        """Forward pass of the classifier.

        :param input_ids: Input token IDs
        :type input_ids: torch.LongTensor, optional
        :param attention_mask: Mask to avoid performing attention on padding token indices, defaults to None
        :type attention_mask: torch.FloatTensor, optional
        :param token_type_ids: Segment token indices to indicate first and second portions of the inputs, defaults to None
        :type token_type_ids: torch.LongTensor, optional
        :param position_ids: Indices of positions of each input sequence, defaults to None
        :type position_ids: torch.LongTensor, optional
        :param head_mask: Mask to nullify selected heads of the self-attention modules, defaults to None
        :type head_mask: torch.FloatTensor, optional
        :param inputs_embeds: Alternative to input_ids, allows direct input of embeddings, defaults to None
        :type inputs_embeds: torch.FloatTensor, optional
        :param labels: Target labels, defaults to None
        :type labels: torch.LongTensor, optional
        :param output_attentions: Whether or not to return the attentions tensors of all attention layers, defaults to None
        :type output_attentions: bool, optional
        :param output_hidden_states: Whether or not to return the hidden states tensors of all layers, defaults to None
        :type output_hidden_states: bool, optional
        :param return_dict: Whether or not to return a dictionary, defaults to None
        :type return_dict: bool, optional
        :param cls_output: Whether or not to return the classifier output, defaults to None
        :type cls_output: bool, optional
        :return: Classifier output if cls_output is True, otherwise returns loss and logits
        :rtype: Union[SequenceClassifierOutput, Tuple[torch.Tensor, torch.Tensor]]
        """

        # Forward pass through Roberta model
        outputs = self.roberta(
            input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict
        )

        x = outputs[0][:, 0, :] # take <s> token (equiv. to [CLS])
        x = self.dropout(x)
        logits = self.dense(x)
        
        loss = None
        if labels is not None:
            loss = self.loss_func(logits, labels)

        if cls_output:
            return SequenceClassifierOutput(
                loss=loss,
                logits=logits,
                hidden_states=outputs.hidden_states,
                attentions=outputs.attentions,
            )

        return loss, logits


if __name__ == "__main__":
    model = RobertaClassifier.from_pretrained("SuperAnnotate/ai-detector")
    print(model)

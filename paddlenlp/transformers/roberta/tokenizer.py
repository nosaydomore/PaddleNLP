# Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
# Copyright 2018 The Google AI Language Team Authors and The HuggingFace Inc. team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json
from paddle.utils import try_import

from .. import BasicTokenizer, PretrainedTokenizer, WordpieceTokenizer, GPTTokenizer
from ..gpt.tokenizer import bytes_to_unicode

__all__ = ['RobertaTokenizer', 'RobertaBPETokenizer']


class RobertaTokenizer(PretrainedTokenizer):
    """
    Constructs a RoBerta tokenizer. It uses a basic tokenizer to do punctuation
    splitting, lower casing and so on, and follows a WordPiece tokenizer to
    tokenize as subwords.

    Args:
        vocab_file (str):
            The vocabulary file path (ends with '.txt') required to instantiate
            a `WordpieceTokenizer`.
        do_lower_case (bool):
            Whether or not to lowercase the input when tokenizing.
            Defaults to`True`.
        unk_token (str):
            A special token representing the *unknown (out-of-vocabulary)* token.
            An unknown token is set to be `unk_token` inorder to be converted to an ID.
            Defaults to "[UNK]".
        sep_token (str):
            A special token separating two different sentences in the same input.
            Defaults to "[SEP]".
        pad_token (str):
            A special token used to make arrays of tokens the same size for batching purposes.
            Defaults to "[PAD]".
        cls_token (str):
            A special token used for sequence classification. It is the last token
            of the sequence when built with special tokens. Defaults to "[CLS]".
        mask_token (str):
            A special token representing a masked token. This is the token used
            in the masked language modeling task which the model tries to predict the original unmasked ones.
            Defaults to "[MASK]".

    Examples:
        .. code-block::

            from paddlenlp.transformers import RobertaTokenizer
            tokenizer = RobertaTokenizer.from_pretrained('roberta-wwm-ext')

            tokens = tokenizer('He was a puppeteer')
            #{'input_ids': [101, 9245, 9947, 143, 11227, 9586, 8418, 8854, 8180, 102],
            #'token_type_ids': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}、

    """

    resource_files_names = {"vocab_file": "vocab.txt"}  # for save_pretrained
    pretrained_resource_files_map = {
        "vocab_file": {
            "roberta-wwm-ext":
            "https://paddlenlp.bj.bcebos.com/models/transformers/roberta_base/vocab.txt",
            "roberta-wwm-ext-large":
            "https://paddlenlp.bj.bcebos.com/models/transformers/roberta_large/vocab.txt",
            "rbt3":
            "https://paddlenlp.bj.bcebos.com/models/transformers/rbt3/vocab.txt",
            "rbtl3":
            "https://paddlenlp.bj.bcebos.com/models/transformers/rbtl3/vocab.txt",
            "roberta-base-ft-chinanews-chn":
            "https://huggingface.co/uer/roberta-base-finetuned-chinanews-chinese/resolve/main/vocab.txt",
            "roberta-base-ft-cluener2020-chn":
            "https://huggingface.co/uer/roberta-base-finetuned-cluener2020-chinese/resolve/main/vocab.txt",
            "roberta-base-chn-extractive-qa":
            "https://huggingface.co/uer/roberta-base-chinese-extractive-qa/resolve/main/vocab.txt",
        }
    }
    pretrained_init_configuration = {
        "roberta-wwm-ext": {
            "do_lower_case": True
        },
        "roberta-wwm-ext-large": {
            "do_lower_case": True
        },
        "rbt3": {
            "do_lower_case": True
        },
        "rbtl3": {
            "do_lower_case": True
        },
        "roberta-base-ft-chinanews-chn": {
            "do_lower_case": True
        },
        "roberta-base-ft-cluener2020-chn": {
            "do_lower_case": True
        },
        "roberta-base-chn-extractive-qa": {
            "do_lower_case": True
        },
    }

    def __init__(self,
                 vocab_file,
                 do_lower_case=True,
                 unk_token="[UNK]",
                 sep_token="[SEP]",
                 pad_token="[PAD]",
                 cls_token="[CLS]",
                 mask_token="[MASK]"):

        if not os.path.isfile(vocab_file):
            raise ValueError(
                "Can't find a vocabulary file at path '{}'. To load the "
                "vocabulary from a pretrained model please use "
                "`tokenizer = RobertaTokenizer.from_pretrained(PRETRAINED_MODEL_NAME)`"
                .format(vocab_file))
        self.do_lower_case = do_lower_case
        self.vocab = self.load_vocabulary(vocab_file, unk_token=unk_token)
        self.basic_tokenizer = BasicTokenizer(do_lower_case=do_lower_case)
        self.wordpiece_tokenizer = WordpieceTokenizer(
            vocab=self.vocab, unk_token=unk_token)

    @property
    def vocab_size(self):
        """
        Return the size of vocabulary.

        Returns:
            int: The size of vocabulary.
        """

        return len(self.vocab)

    def _tokenize(self, text):
        """
        End-to-end tokenization for RoBERTa models.

        Args:
            text (str): The text to be tokenized.

        Returns:
            list: A list of string representing converted tokens.
        """
        split_tokens = []
        for token in self.basic_tokenizer.tokenize(text):
            for sub_token in self.wordpiece_tokenizer.tokenize(token):
                split_tokens.append(sub_token)
        return split_tokens

    def tokenize(self, text):
        """
        Converts a string to a list of tokens.

        Args:
            text (str): The text to be tokenized.

        Returns:
            List(str): A list of string representing converted tokens.

        Examples:
            .. code-block::

                from paddlenlp.transformers import RobertaTokenizer

                tokenizer = RobertaTokenizer.from_pretrained('roberta-wwm-ext')
                tokens = tokenizer.tokenize('He was a puppeteer')

        """

        return self._tokenize(text)

    def convert_tokens_to_string(self, tokens):
        """
        Converts a sequence of tokens (list of string) to a single string. Since
        the usage of WordPiece introducing `##` to concat subwords, also removes
        `##` when converting.

        Args:
            tokens (list): A list of string representing tokens to be converted.

        Returns:
            str: Converted string from tokens.

        Examples:
            .. code-block::

                from paddlenlp.transformers import RobertaTokenizer

                tokenizer = RobertaTokenizer.from_pretrained('roberta-wwm-ext')
                tokens = tokenizer.tokenize('He was a puppeteer')
                strings = tokenizer.convert_tokens_to_string(tokens)
                '''
                he was a puppeteer
                '''

        """
        out_string = " ".join(tokens).replace(" ##", "").strip()
        return out_string

    def num_special_tokens_to_add(self, pair=False):
        """
        Returns the number of added tokens when encoding a sequence with special tokens.

        Args:
            pair(bool):
                Whether the input is a sequence pair or a single sequence.
                Defaults to `False` and the input is a single sequence.

        Returns:
            int: Number of tokens added to sequences.
        """
        token_ids_0 = []
        token_ids_1 = []
        return len(
            self.build_inputs_with_special_tokens(token_ids_0, token_ids_1
                                                  if pair else None))

    def build_inputs_with_special_tokens(self, token_ids_0, token_ids_1=None):
        """
        Build model inputs from a sequence or a pair of sequence for sequence classification tasks by concatenating and
        adding special tokens.

        A RoBERTa sequence has the following format:

        - single sequence:       ``[CLS] X [SEP]``
        - pair of sequences:        ``[CLS] A [SEP] B [SEP]``

        Args:
            token_ids_0 (List[int]):
                List of IDs to which the special tokens will be added.
            token_ids_1 (List[int], optional):
                Optional second list of IDs for sequence pairs.
                Defaults to `None`.

        Returns:
            List[int]: List of input_id with the appropriate special tokens.
        """
        if token_ids_1 is None:
            return [self.cls_token_id] + token_ids_0 + [self.sep_token_id]
        _cls = [self.cls_token_id]
        _sep = [self.sep_token_id]
        return _cls + token_ids_0 + _sep + token_ids_1 + _sep

    def build_offset_mapping_with_special_tokens(self,
                                                 offset_mapping_0,
                                                 offset_mapping_1=None):
        """
        Build offset map from a pair of offset map by concatenating and adding offsets of special tokens.

        A RoBERTa offset_mapping has the following format:

        - single sequence:      ``(0,0) X (0,0)``
        - pair of sequences:        ``(0,0) A (0,0) B (0,0)``

        Args:
            offset_mapping_ids_0 (List[tuple]):
                List of wordpiece offsets to which the special tokens will be added.
            offset_mapping_ids_1 (List[tuple], optional):
                Optional second list of wordpiece offsets for offset mapping pairs. Defaults to None.

        Returns:
            List[tuple]: A list of wordpiece offsets with the appropriate offsets of special tokens.
        """
        if offset_mapping_1 is None:
            return [(0, 0)] + offset_mapping_0 + [(0, 0)]

        return [(0, 0)] + offset_mapping_0 + [(0, 0)
                                              ] + offset_mapping_1 + [(0, 0)]

    def create_token_type_ids_from_sequences(self,
                                             token_ids_0,
                                             token_ids_1=None):
        """
        Create a mask from the two sequences passed to be used in a sequence-pair classification task.

        A RoBERTa sequence pair mask has the following format:
        ::

            0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1
            | first sequence    | second sequence |

        If :obj:`token_ids_1` is :obj:`None`, this method only returns the first portion of the mask (0s).

        Args:
            token_ids_0 (List[int]):
                A list of `inputs_ids` for the first sequence.
            token_ids_1 (List[int], optional):
                Optional second list of IDs for sequence pairs. Defaults to None.

        Returns:
            List[int]: List of token_type_id according to the given sequence(s).
        """
        _sep = [self.sep_token_id]
        _cls = [self.cls_token_id]
        if token_ids_1 is None:
            return len(_cls + token_ids_0 + _sep) * [0]
        return len(_cls + token_ids_0 + _sep) * [0] + len(token_ids_1 +
                                                          _sep) * [1]

    def get_special_tokens_mask(self,
                                token_ids_0,
                                token_ids_1=None,
                                already_has_special_tokens=False):
        """
        Retrieves sequence ids from a token list that has no special tokens added. This method is called when adding
        special tokens using the tokenizer ``encode`` methods.

        Args:
            token_ids_0 (List[int]):
                A list of `inputs_ids` for the first sequence.
            token_ids_1 (List[int], optinal):
                Optional second list of IDs for sequence pairs. Defaults to None.
            already_has_special_tokens (bool, optional): Whether or not the token list is already
                formatted with special tokens for the model. Defaults to None.

        Returns:
            List[int]: The list of integers either be 0 or 1: 1 for a special token, 0 for a sequence token.
        """

        if already_has_special_tokens:
            if token_ids_1 is not None:
                raise ValueError(
                    "You should not supply a second sequence if the provided sequence of "
                    "ids is already formatted with special tokens for the model."
                )
            return list(
                map(lambda x: 1 if x in [self.sep_token_id, self.cls_token_id] else 0,
                    token_ids_0))

        if token_ids_1 is not None:
            return [1] + ([0] * len(token_ids_0)) + [1] + (
                [0] * len(token_ids_1)) + [1]
        return [1] + ([0] * len(token_ids_0)) + [1]


class RobertaBPETokenizer(GPTTokenizer):
    """
    Constructs a Roberta tokenizer based on byte-level Byte-Pair-Encoding.

    This tokenizer inherits from :class:`~paddlenlp.transformers.GPTTokenizer`
    which contains most of the main methods. For more information regarding those methods,
    please refer to this superclass.

    Args:
        vocab_file (str):
            Path to the vocab file.
            The vocab file contains a mapping from vocabulary strings to indices.
        merges_file (str):
            Path to the merge file.
            The merge file is used to split the input sentence into "subword" units.
            The vocab file is then used to encode those units as intices.
        errors (str):
            Paradigm to follow when decoding bytes to UTF-8.
            Defaults to `'replace'`.
        max_len (int, optional):
            The maximum value of the input sequence length.
            Defaults to `None`.
        special_tokens (list, optional):
            A list of special tokens not in the vocabulary.
            Defaults to `None`.

    Examples:
        .. code-block::

            from paddlenlp.transformers import RobertaBPETokenizer
            tokenizer = RobertaBPETokenizer.from_pretrained('roberta-en-base')

            tokens = tokenizer('This is a simple Paddle')
            #{'input_ids': [0, 713, 16, 10, 2007, 221, 33151, 2],
            #'token_type_ids': [0, 0, 0, 0, 0, 0, 0, 0]}、

    """
    resource_files_names = {
        "vocab_file": "vocab.json",
        "merges_file": "merges.txt"
    }  # for save_pretrained
    roberta_en_base_vocab_link = "https://huggingface.co/roberta-base/resolve/main/vocab.json"
    roberta_en_base_merges_link = "https://huggingface.co/roberta-base/resolve/main/merges.txt"
    pretrained_resource_files_map = {
        "vocab_file": {
            "roberta-en-base": roberta_en_base_vocab_link,
            "roberta-en-large": roberta_en_base_vocab_link,
            "roberta-base-squad2": roberta_en_base_vocab_link,
            "tiny-distilroberta-base":
            "https://huggingface.co/sshleifer/tiny-distilroberta-base/resolve/main/vocab.json"
        },
        "merges_file": {
            "roberta-en-base": roberta_en_base_merges_link,
            "roberta-en-large": roberta_en_base_merges_link,
            "roberta-base-squad2": roberta_en_base_merges_link,
            "tiny-distilroberta-base":
            "https://huggingface.co/sshleifer/tiny-distilroberta-base/resolve/main/merges.txt"
        }
    }
    pretrained_init_configuration = {
        "roberta-en-base": {},
        "roberta-en-large": {},
        "roberta-base-squad2": {},
        "tiny-distilroberta-base": {}
    }

    def __init__(
            self,
            vocab_file,
            merges_file,
            errors='replace',
            max_len=None,
            special_tokens=None,
            bos_token="<s>",
            eos_token="</s>",
            cls_token="<s>",
            sep_token="</s>",
            unk_token="<unk>",
            pad_token="<pad>",
            mask_token="<mask>", ):

        self._vocab_file = vocab_file
        self._merges_file = merges_file
        self.max_len = max_len if max_len is not None else int(1e12)
        self.num_command_tokens = 2
        self.num_type_tokens = 2

        with open(vocab_file, encoding="utf-8") as vocab_handle:
            self.encoder = json.load(vocab_handle)
        self.decoder = {v: k for k, v in self.encoder.items()}

        self.num_tokens = len(self.encoder)
        self.num_text_tokens = self.num_tokens - 1
        self.errors = errors  # how to handle errors in decoding
        self.byte_encoder = bytes_to_unicode()
        self.byte_decoder = {v: k for k, v in self.byte_encoder.items()}
        with open(merges_file, encoding="utf-8") as merges_handle:
            bpe_data = merges_handle.read().split('\n')[1:-1]
        bpe_merges = [tuple(merge.split()) for merge in bpe_data]
        self.bpe_ranks = dict(zip(bpe_merges, range(len(bpe_merges))))
        self.cache = {}
        re = try_import("regex")
        self.pat = re.compile(
            r"""'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
        )

        self.special_tokens = {}
        self.special_tokens_decoder = {}
        self.set_special_tokens(special_tokens)

    def build_inputs_with_special_tokens(self, token_ids_0, token_ids_1=None):
        """
        Build model inputs from a sequence or a pair of sequence for sequence classification
        tasks by concatenating and adding special tokens.
        """
        _cls = [self.cls_token_id]
        _sep = [self.sep_token_id]
        if token_ids_1 is None:
            return _cls + token_ids_0 + _sep
        return _cls + token_ids_0 + _sep + _sep + token_ids_1 + _sep

    def get_offset_mapping(self, text):
        tokens = self._tokenize(text)
        offset_mapping = []
        offset = 0
        for token in tokens:
            if token[0] == 'Ġ':
                offset_mapping.append((offset + 1, offset + len(token)))
            else:
                offset_mapping.append((offset, offset + len(token)))
            offset += len(token)

        return offset_mapping

    def build_offset_mapping_with_special_tokens(self, offset_mapping_0,
                                                 offset_mapping_1):
        """
        Build offset map from a pair of offset map by concatenating and adding offsets of special tokens.

        A Roberta offset_mapping has the following format:

        - single sequence:      ``(0,0) X (0,0)``
        - pair of sequences:        ``(0,0) A (0,0) (0,0) B (0,0)``

        Args:
            offset_mapping_ids_0 (List[tuple]):
                List of wordpiece offsets to which the special tokens will be added.
            offset_mapping_ids_1 (List[tuple], optional):
                Optional second list of wordpiece offsets for offset mapping pairs. Defaults to None.

        Returns:
            List[tuple]: A list of wordpiece offsets with the appropriate offsets of special tokens.
        """
        if offset_mapping_1 is None:
            return [(0, 0)] + offset_mapping_0 + [(0, 0)]

        return [(0, 0)] + offset_mapping_0 + [(0, 0), (0, 0)
                                              ] + offset_mapping_1 + [(0, 0)]

    def get_special_tokens_mask(self,
                                token_ids_0,
                                token_ids_1=None,
                                already_has_special_tokens=False):
        """
        Retrieves sequence ids from a token list that has no special tokens added. This method is called when adding
        special tokens using the tokenizer ``encode`` methods.

        Args:
            token_ids_0 (List[int]):
                A list of `inputs_ids` for the first sequence.
            token_ids_1 (List[int], optinal):
                Optional second list of IDs for sequence pairs. Defaults to None.
            already_has_special_tokens (bool, optional): Whether or not the token list is already 
                formatted with special tokens for the model. Defaults to None.

        Returns:
            List[int]: The list of integers either be 0 or 1: 1 for a special token, 0 for a sequence token.
        """

        if already_has_special_tokens:
            return super().get_special_tokens_mask(
                token_ids_0=token_ids_0,
                token_ids_1=token_ids_1,
                already_has_special_tokens=True)

        if token_ids_1 is None:
            return [1] + ([0] * len(token_ids_0)) + [1]
        return [1] + ([0] * len(token_ids_0)) + [1, 1] + ([0] * len(token_ids_1)
                                                          ) + [1]

    def create_token_type_ids_from_sequences(self, token_ids_0, token_ids_1):
        sep = [self.sep_token_id]
        cls = [self.cls_token_id]

        if token_ids_1 is None:
            return len(cls + token_ids_0 + sep) * [0]
        return len(cls + token_ids_0 + sep + sep + token_ids_1 + sep) * [0]

    def convert_tokens_to_string(self, tokens):
        text = ''.join(tokens)
        text = bytearray([self.byte_decoder[c] for c in text]).decode(
            'utf-8', errors=self.errors)
        return text

    def convert_ids_to_tokens(self, ids, skip_special_tokens=False):
        """
        Converts an index or a sequence indices to a single
        token or a sequence of tokens.

        Args:
            ids (int|List[int]):
                The token id (or token ids) to be converted to text.
            skip_special_tokens (bool, optional):
                Whether or not to skip the special tokens.
                Defaults to `False`, which means we don't skip the special tokens.

        Returns:
            str|List[str]: The converted token or the sequence of tokens.
        """

        tokens = [self.decoder[id] for id in ids]
        if skip_special_tokens and isinstance(tokens, list):
            tokens = [
                token for token in tokens
                if token not in self.all_special_tokens
            ]
        return tokens

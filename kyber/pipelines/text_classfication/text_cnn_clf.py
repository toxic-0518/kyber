# -*- coding: utf-8 -*-
# Pipeline example for text cnn classification model using THUCNews Data
"""
    Task:   Text Classification
    Model:  Text CNN (native Kim)
    Data:   THUCNews
"""
import os
import tensorflow as tf
from config import *
from utils import *
from models import TextCNN
from modules.pipeline import Pipeline
from modules.evaluator import Evaluator4Clf
from tensorflow.python.keras.callbacks import TensorBoard

class TextCNNPipeline(Pipeline):
    def build_field(self):
        news_txt_field = Field(name='text', tokenizer=CharTokenizer, seq_flag=True, fix_length=512)
        label_filed = Field(name='label', tokenizer=None, seq_flag=False, is_target=True, categorical=True,
                            num_classes=10)
        self.fields_dict = {"text": news_txt_field, "label": label_filed}
        self.vocab_group = [["text"]]

    def build_model(self):
        self.model = TextCNN(vocab_size=len(self.fields_dict['text'].vocab),
                             embedding_dim=100,
                             num_classes=10,
                             seq_len=512)

        # self.model.build((None, 512))
        self.model.summary()

    def train(self, epochs, callbacks):
        """
         Build model, loss, optimizer and train
        :param epochs: number of epochs in training
        :param callbacks:
        :return:
        """
        opt = tf.keras.optimizers.Adam(learning_rate=0.001)
        self.model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
        self.model.fit(self.train_iter.forfit(), steps_per_epoch=len(self.train_iter), epochs=epochs, \
                            validation_data=self.dev_iter.forfit(), validation_steps=len(self.dev_iter),
                            callbacks=callbacks)



def train():
    text_cnn_pipeline = TextCNNPipeline(raw_data=Config.thu_news_raw_data, \
                                        standard_data = os.path.join(Config.thu_news_standard_data,Config.standard_filename_clf),
                                        processor_cls=THUCNewsProcessor,
                                        dataloader_cls=ClassifierLoader)

    evaluator = Evaluator4Clf(text_cnn_pipeline, Config.text_cnn_thucnews_log_path, Config.text_cnn_thucnews_model_path)
    tb_callback = TensorBoard(log_dir=Config.text_cnn_thucnews_log_path)

    text_cnn_pipeline.build(data_refresh=True)
    text_cnn_pipeline.train(epochs=10, callbacks=[evaluator, tb_callback])
    # model_name = "model.weights"
    ## evaluate on test data loader
    text_cnn_pipeline.test()
    # text_cnn_pipeline.save(Config.text_cnn_thucnews_model_path, model_name, fields_save=True, weights_only=True)


def predict():
    text_cnn_pipeline = TextCNNPipeline()
    text_cnn_pipeline.load_model(Config.text_cnn_thucnews_model_path, "model.weights")
    # text_cnn_pipeline.build()
    res = text_cnn_pipeline.inference(["我想去打篮球"],row_type="list")
    print(res.argmax())

if __name__ == '__main__':
    train()
    # predict()










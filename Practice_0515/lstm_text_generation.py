{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Example script to generate text from Nietzsche's writings.\n",
    "\n",
    "At least 20 epochs are required before the generated text\n",
    "starts sounding coherent.\n",
    "\n",
    "It is recommended to run this script on GPU, as recurrent\n",
    "networks are quite computationally intensive.\n",
    "\n",
    "If you try this script on new data, make sure your corpus\n",
    "has at least ~100k characters. ~1M is better."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "from keras.callbacks import LambdaCallback\n",
    "from keras.models import Sequential\n",
    "from keras.layers import Dense, Activation\n",
    "from keras.layers import LSTM\n",
    "from keras.optimizers import RMSprop\n",
    "from keras.utils.data_utils import get_file\n",
    "import numpy as np\n",
    "import random\n",
    "import sys\n",
    "import io"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Downloading data from https://s3.amazonaws.com/text-datasets/nietzsche.txt\n",
      "581632/600901 [============================>.] - ETA: 0s"
     ]
    }
   ],
   "source": [
    "path = get_file('nietzsche.txt', origin='https://s3.amazonaws.com/text-datasets/nietzsche.txt')\n",
    "with io.open(path, encoding='utf-8') as f:\n",
    "    text = f.read().lower()\n",
    "print('corpus length:', len(text))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "chars = sorted(list(set(text)))\n",
    "print('total chars:', len(chars))\n",
    "char_indices = dict((c, i) for i, c in enumerate(chars))\n",
    "indices_char = dict((i, c) for i, c in enumerate(chars))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "# cut the text in semi-redundant sequences of maxlen characters\n",
    "maxlen = 40\n",
    "step = 3\n",
    "sentences = []\n",
    "next_chars = []\n",
    "for i in range(0, len(text) - maxlen, step):\n",
    "    sentences.append(text[i: i + maxlen])\n",
    "    next_chars.append(text[i + maxlen])\n",
    "print('nb sequences:', len(sentences))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "print('Vectorization...')\n",
    "x = np.zeros((len(sentences), maxlen, len(chars)), dtype=np.bool)\n",
    "y = np.zeros((len(sentences), len(chars)), dtype=np.bool)\n",
    "for i, sentence in enumerate(sentences):\n",
    "    for t, char in enumerate(sentence):\n",
    "        x[i, t, char_indices[char]] = 1\n",
    "    y[i, char_indices[next_chars[i]]] = 1"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "# build the model: a single LSTM\n",
    "print('Build model...')\n",
    "model = Sequential()\n",
    "model.add(LSTM(128, input_shape=(maxlen, len(chars))))\n",
    "model.add(Dense(len(chars)))\n",
    "model.add(Activation('softmax'))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "optimizer = RMSprop(lr=0.01)\n",
    "model.compile(loss='categorical_crossentropy', optimizer=optimizer)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "def sample(preds, temperature=1.0):\n",
    "    # helper function to sample an index from a probability array\n",
    "    preds = np.asarray(preds).astype('float64')\n",
    "    preds = np.log(preds) / temperature\n",
    "    exp_preds = np.exp(preds)\n",
    "    preds = exp_preds / np.sum(exp_preds)\n",
    "    probas = np.random.multinomial(1, preds, 1)\n",
    "    return np.argmax(probas)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "def on_epoch_end(epoch, logs):\n",
    "    # Function invoked at end of each epoch. Prints generated text.\n",
    "    print()\n",
    "    print('----- Generating text after Epoch: %d' % epoch)\n",
    "\n",
    "    start_index = random.randint(0, len(text) - maxlen - 1)\n",
    "    for diversity in [0.2, 0.5, 1.0, 1.2]:\n",
    "        print('----- diversity:', diversity)\n",
    "\n",
    "        generated = ''\n",
    "        sentence = text[start_index: start_index + maxlen]\n",
    "        generated += sentence\n",
    "        print('----- Generating with seed: \"' + sentence + '\"')\n",
    "        sys.stdout.write(generated)\n",
    "\n",
    "        for i in range(400):\n",
    "            x_pred = np.zeros((1, maxlen, len(chars)))\n",
    "            for t, char in enumerate(sentence):\n",
    "                x_pred[0, t, char_indices[char]] = 1.\n",
    "\n",
    "            preds = model.predict(x_pred, verbose=0)[0]\n",
    "            next_index = sample(preds, diversity)\n",
    "            next_char = indices_char[next_index]\n",
    "\n",
    "            generated += next_char\n",
    "            sentence = sentence[1:] + next_char\n",
    "\n",
    "            sys.stdout.write(next_char)\n",
    "            sys.stdout.flush()\n",
    "        print()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "print_callback = LambdaCallback(on_epoch_end=on_epoch_end)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "collapsed": true
   },
   "outputs": [],
   "source": [
    "model.fit(x, y,\n",
    "          batch_size=128,\n",
    "          epochs=60,\n",
    "          callbacks=[print_callback])"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.6.3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}

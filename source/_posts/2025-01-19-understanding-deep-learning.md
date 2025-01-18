---
id: understanding-deep-learning
title: "《Understanding Deep Learning》书摘"
description: "08/05/24 版，图解 Deep Learning"
date: 2025.01.19 10:34
categories:
    - Book
tags: [Book]
keywords: Deep Learning, Supervised Learning, Unsupervised Learning, Reinforcement Learning, Neural Networks, Convolutional Neural Networks (CNN), Residual Networks (ResNet), Self-Attention, Generative Adversarial Networks (GAN), Variational Autoencoders (VAE)
cover: /contents/understanding-deep-learning/cover.jpg
---

[豆瓣](https://book.douban.com/subject/36395283/)

最新版本电子版下载地址：https://udlbook.github.io/udlbook/

# Chapter 1 Introduction

> Machine learning methods can coarsely be divided into three areas: supervised, unsupervised, and reinforcement learning.

## 1.1 Supervised learning

> ![1.1](/contents/understanding-deep-learning/1.1.png)
> 
> Figure 1.1 Machine learning is an area of artificial intelligence that fits mathematical models to observed data. It can coarsely be divided into supervised learning, unsupervised learning, and reinforcement learning. Deep neural networks contribute to each of these areas.

# Chapter 3 Shallow neural networks

## 3.1 Neural network example

> ![3.1](/contents/understanding-deep-learning/3.1.png)
>
> Figure 3.1 Rectified linear unit (ReLU). This activation function returns zero if the input is less than zero and returns the input unchanged otherwise. In other words, it clips negative values to zero. Note that there are many other possible choices for the activation function (see figure 3.13), but the ReLU is the most commonly used and the easiest to understand.

### 3.1.2 Depicting neural networks

> ![3.4](/contents/understanding-deep-learning/3.4.png)
> 
> Figure 3.4 Depicting neural networks. a) The input x is on the left, the hidden units h1 , h2 , and h3 in the center, and the output y on the right. Computation flows from left to right. The input is used to compute the hidden units, which are combined to create the output. Each of the ten arrows represents a parameter (intercepts in orange and slopes in black). Each parameter multiplies its source and adds the result to its target. For example, we multiply the parameter φ1 by source h1 and add it to y. We introduce additional nodes containing ones (orange circles) to incorporate the offsets into this scheme, so we multiply φ0 by one (with no effect) and add it to y. ReLU functions are applied at the hidden units. b) More typically, the intercepts, ReLU functions, and parameter names are omitted; this simpler depiction represents the same network.

## 3.2 Universal approximation theorem

> ![3.5](/contents/understanding-deep-learning/3.5.png)
>
> Figure 3.5 Approximation of a 1D function (dashed line) by a piecewise linear model. a–c) As the number of regions increases, the model becomes closer and closer to the continuous function. A neural network with a scalar input creates one extra linear region per hidden unit. This idea generalizes to functions in Di dimensions. The universal approximation theorem proves that, with enough hidden units, there exists a shallow neural network that can describe any given continuous function defined on a compact subset of RDi to arbitrary precision.

## 3.5 Terminology

> ![3.12](/contents/understanding-deep-learning/3.12.png)
> 
> Figure 3.12 Terminology. A shallow network consists of an input layer, a hidden layer, and an output layer. Each layer is connected to the next by forward connections (arrows). For this reason, these models are referred to as feed-forward networks. When every variable in one layer connects to every variable in the next, we call this a fully connected network. Each connection represents a slope parameter in the underlying equation, and these parameters are termed weights. The variables in the hidden layer are termed neurons or hidden units. The values feeding into the hidden units are termed pre-activations, and the values at the hidden units (i.e., after the ReLU function is applied) are termed activations.

# Chapter 4 Deep neural networks

## 4.2 From composing networks to deep networks

> ![4.3](/contents/understanding-deep-learning/4.3.png)
>
> Figure 4.3 Deep networks as folding input space. a) One way to think about the first network from figure 4.1 is that it “folds” the input space back on top of itself. b) The second network applies its function to the folded space. c) The final output is revealed by “unfolding” again.

## 4.3 Deep neural networks

### 4.3.1 Hyperparameters

> The number of hidden units in each layer is referred to as the width of the network, and the number of hidden layers as the depth. The total number of hidden units is a measure of the network’s capacity.

> ![4.6](/contents/understanding-deep-learning/4.6.png)
> 
> Figure 4.6 Matrix notation for network with Di = 3-dimensional input x, Do = 2-dimensional output y, and K = 3 hidden layers h1 , h2 , and h3 of dimensions D1 = 4, D2 = 2, and D3 = 3 respectively. The weights are stored in matrices Ωk that multiply the activations from the preceding layer to create the pre-activations at the subsequent layer. For example, the weight matrix Ω1 that computes the pre-activations at h2 from the activations at h1 has dimension 2 × 4. It is applied to the four hidden units in layer one and creates the inputs to the two hidden units at layer two. The biases are stored in vectors βk and have the dimension of the layer into which they feed. For example, the bias vector β2 is length three because layer h3 contains three hidden units.

# Chapter 5 Loss functions

## 5.4 Example 2: binary classification

> ![5.7](/contents/understanding-deep-learning/5.7.png)
>
> Figure 5.7 Logistic sigmoid function. This function maps the real line z ∈ R to numbers between zero and one, so sig[z] ∈ [0, 1]. An input of 0 is mapped to 0.5. Negative inputs are mapped to numbers below 0.5, and positive inputs to numbers above 0.5.

# Chapter 6 Fitting models

## 6.1 Gradient descent

### 6.1.2 Gabor model example

> ![6.2](/contents/understanding-deep-learning/6.2.png)
> 
> Figure 6.2 Gabor model. This nonlinear model maps scalar input x to scalar output y and has parameters φ = [φ0 , φ1 ]T . It describes a sinusoidal function that decreases in amplitude with distance from its center. Parameter φ0 ∈ R determines the position of the center. As φ0 increases, the function moves left. Parameter φ1 ∈ R+ squeezes the function along the x-axis relative to the center. As φ1 increases, the function narrows. a–c) Model with different parameters. (Interactive figure)

### 6.1.3 Local minima and saddle points

> ![6.5](/contents/understanding-deep-learning/6.5.png)
> 
> Figure 6.5 Gradient descent vs. stochastic gradient descent. a) Gradient descent with line search. As long as the gradient descent algorithm is initialized in the right “valley” of the loss function (e.g., points 1 and 3), the parameter estimate will move steadily toward the global minimum. However, if it is initialized outside this valley (e.g., point 2), it will descend toward one of the local minima. b) Stochastic gradient descent adds noise to the optimization process, so it is possible to escape from the wrong valley (e.g., point 2) and still reach the global minimum.

## 6.2 Stochastic gradient descent

### 6.2.1 Batches and epochs

> The mechanism for introducing randomness is simple. At each iteration, the algorithm chooses a random subset of the training data and computes the gradient from these examples alone. This subset is known as a minibatch or batch for short.

## 6.3 Momentum

### 6.3.1 Nesterov accelerated momentum

> ![6.7](/contents/understanding-deep-learning/6.7.png)
> 
> Figure 6.7 Stochastic gradient descent with momentum. a) Regular stochastic descent takes a very indirect path toward the minimum. b) With a momentum term, the change at the current step is a weighted combination of the previous change and the gradient computed from the batch. This smooths out the trajectory and increases the speed of convergence.

> ![6.8](/contents/understanding-deep-learning/6.8.png)
> 
> Figure 6.8 Nesterov accelerated momentum. The solution has traveled along the dashed line to arrive at point 1. A traditional momentum update measures the gradient at point 1, moves some distance in this direction to point 2, and then adds the momentum term from the previous iteration (i.e., in the same direction as the dashed line), arriving at point 3. The Nesterov momentum update first applies the momentum term (moving from point 1 to point 4) and then measures the gradient and applies an update to arrive at point 5.

## 6.4 Adam

> ![6.9](/contents/understanding-deep-learning/6.9.png)
> 
> Figure 6.9 Adaptive moment estimation (Adam). a) This loss function changes quickly in the vertical direction but slowly in the horizontal direction. If we run full-batch gradient descent with a learning rate that makes good progress in the vertical direction, then the algorithm takes a long time to reach the final horizontal position. b) If the learning rate is chosen so that the algorithm makes good progress in the horizontal direction, it overshoots in the vertical direction and becomes unstable. c) A straightforward approach is to move a fixed distance along each axis at each step so that we move downhill in both directions. This is accomplished by normalizing the gradient magnitude and retaining only the sign. However, this does not usually converge to the exact minimum but instead oscillates back and forth around it (here between the last two points). d) The Adam algorithm uses momentum in both the estimated gradient and the normalization term, which creates a smoother path.

## 6.5 Training algorithm hyperparameters

> The choices of learning algorithm, batch size, learning rate schedule, and momentum coeﬀicients are all considered hyperparameters of the training algorithm; these directly affect the final model performance but are distinct from the model parameters. Choosing these can be more art than science, and it’s common to train many models with different hyperparameters and choose the best one. This is known as hyperparameter search.

## 6.6 Summary

> ![6.10](/contents/understanding-deep-learning/6.10.png)
> 
> Figure 6.10 Line search using the bracketing approach. a) The current solution is at position a (orange point), and we wish to search the region [a, d] (gray shaded area). We define two points b, c interior to the search region and evaluate the loss function at these points. Here L[b] > L[c], so we eliminate the range [a, b]. b) We now repeat this procedure in the refined search region and find that L[b] < L[c], so we eliminate the range [c, d]. c) We repeat this process until this minimum is closely bracketed.

# Chapter 8 Measuring performance

## 8.2 Sources of error

> ![8.5](/contents/understanding-deep-learning/8.5.png)
> 
> Figure 8.5 Sources of test error. a) Noise. Data generation is noisy, so even if the model exactly replicates the true underlying function (black line), the noise in the test data (gray points) means that some error will remain (gray region represents two standard deviations). b) Bias. Even with the best possible parameters, the three-region model (cyan line) cannot exactly fit the true function (black line). This bias is another source of error (gray regions represent signed error). c) Variance. In practice, we have limited noisy training data (orange points). When we fit the model, we don’t recover the best possible function from panel (b) but a slightly different function (cyan line) that reflects idiosyncrasies of the training data. This provides an additional source of error (gray region represents two standard deviations). Figure 8.6 shows how this region was calculated.

### 8.2.1 Noise, bias, and variance

> There are three possible sources of error, which are known as noise, bias, and variance respectively (figure 8.5):

## 8.3 Reducing error

### 8.3.3 Bias-variance trade-off

> For a fixed-size training dataset, the variance term typically increases as the model capacity increases. Consequently, increasing the model capacity does not necessarily reduce the test error. This is known as the bias-variance trade-off.

## 8.6 Summary

> To measure performance, we use a separate test set. The degree to which performance is maintained on this test set is known as generalization. Test errors can be explained by three factors: noise, bias, and variance. These combine additively in regression problems with least squares losses. Adding training data decreases the variance. When the model capacity is less than the number of training examples, increasing the capacity decreases bias but increases variance. This is known as the bias-variance trade-off, and there is a capacity where the trade-off is optimal.

> However, this is balanced against a tendency for performance to improve with capacity, even when the parameters exceed the training examples. Together, these two phenomena create the double descent curve. It is thought that the model interpolates more smoothly between the training data points in the over-parameterized “modern regime,” although it is unclear what drives this. To choose the capacity and other model and training algorithm hyperparameters, we fit multiple models and evaluate their performance using a separate validation set.

> Cross-validation: 
>
> We saw that it is typical to divide the data into three parts: training data (which is used to learn the model parameters), validation data (which is used to choose the hyperparameters), and test data (which is used to estimate the final performance). This approach is known as cross-validation. However, this division may cause problems where the total number of data examples is limited; if the number of training examples is comparable to the model capacity, then the variance will be large.
> 
> One way to mitigate this problem is to use k-fold cross-validation. The training and validation data are partitioned into K disjoint subsets. For example, we might divide these data into five parts. We train with four and validate with the fifth for each of the five permutations and choose the hyperparameters based on the average validation performance. The final test performance is assessed using the average of the predictions from the five models with the best hyperparameters on an entirely different test set. There are many variations of this idea, but all share the general goal of using a larger proportion of the data to train the model, thereby reducing variance.

# Chapter 9 Regularization

## 9.1 Explicit regularization

### 9.1.2 L2 regularization

> ![9.2](/contents/understanding-deep-learning/9.2.png)
> 
> Figure 9.2 L2 regularization in simplified network with 14 hidden units (see figure 8.4). a–f) Fitted functions as we increase the regularization coeﬀicient λ. The black curve is the true function, the orange circles are the noisy training data, and the cyan curve is the fitted model. For small λ (panels a–b), the fitted function passes exactly through the data points. For intermediate λ (panels c–d), the function is smoother and more similar to the ground truth. For large λ (panels e–f), the regularization term overpowers the likelihood term, so the fitted function is too smooth and the overall fit is worse.

## 9.3 Heuristics to improve performance

### 9.3.2 Ensembling

> ![9.6](/contents/understanding-deep-learning/9.6.png)
>
> Figure 9.6 Early stopping. a) Simplified shallow network model with 14 linear regions (figure 8.4) is initialized randomly (cyan curve) and trained with SGD using a batch size of five and a learning rate of 0.05. b–d) As training proceeds, the function first captures the coarse structure of the true function (black curve) before e–f) overfitting to the noisy training data (orange points). Although the training loss continues to decrease throughout this process, the learned models in panels (c) and (d) are closest to the true underlying function. They will generalize better on average to test data than those in panels (e) or (f).

> ![9.7](/contents/understanding-deep-learning/9.7.png)
> 
> Figure 9.7 Ensemble methods. a) Fitting a single model (gray curve) to the entire dataset (orange points). b–e) Four models created by re-sampling the data with replacement (bagging) four times (size of orange point indicates number of times the data point was re-sampled). f) When we average the predictions of this ensemble, the result (cyan curve) is smoother than the result from panel (a) for the full dataset (gray curve) and will probably generalize better.

### 9.3.3 Dropout

> ![9.8](/contents/understanding-deep-learning/9.8.png)
> 
> Figure 9.8 Dropout. a) Original network. b–d) At each training iteration, a random subset of hidden units is clamped to zero (gray nodes). The result is that the incoming and outgoing weights from these units have no effect, so we are training with a slightly different network each time.

> ![9.9](/contents/understanding-deep-learning/9.9.png)
> 
> Figure 9.9 Dropout mechanism. a) An undesirable kink in the curve is caused by a sequential increase in the slope, decrease in the slope (at circled joint), and then another increase to return the curve to its original trajectory. Here we are using full-batch gradient descent, and the model (from figure 8.4) fits the data as well as possible, so further training won’t remove the kink. b) Consider what happens if we remove the eighth hidden unit that produced the circled joint in panel (a), as might happen using dropout. Without the decrease in the slope, the right-hand side of the function takes an upwards trajectory, and a subsequent gradient descent step will aim to compensate for this change. c) Curve after 2000 iterations of (i) randomly removing one of the three hidden units that cause the kink and (ii) performing a gradient descent step. The kink does not affect the loss but is nonetheless removed by this approximation of the dropout mechanism.

### 9.3.8 Augmentation

> ![9.12](/contents/understanding-deep-learning/9.12.png)
> 
> Figure 9.12 Transfer, multi-task, and self-supervised learning. a) Transfer learning is used when we have limited labeled data for the primary task (here depth estimation) but plentiful data for a secondary task (here segmentation). We train a model for the secondary task, remove the final layers, and replace them with new layers appropriate to the primary task. We then train only the new layers or fine-tune the entire network for the primary task. The network learns a good internal representation from the secondary task that is then exploited for the primary task. b) In multi-task learning, we train a model to perform multiple tasks simultaneously, hoping that performance on each will improve. c) In generative self-supervised learning, we remove part of the data and train the network to complete the missing information. Here, the task is to fill in (inpaint) a masked portion of the image. This permits transfer learning when no labels are available. Images from Cordts et al. (2016).

## 9.4 Summary

> ![9.14](/contents/understanding-deep-learning/9.14.png)
> 
> Figure 9.14 Regularization methods. The regularization methods discussed in this chapter aim to improve generalization by one of four mechanisms. Some methods aim to make the modeled function smoother. Other methods increase the effective amount of data. The third group of methods combine multiple models and hence mitigate against uncertainty in the fitting process. Finally, the fourth group of methods encourages the training process to converge to a wide minimum where small errors in the estimated parameters are less important (see also figure 20.11).

# Chapter 10 Convolutional networks

> Convolutional layers process each local image region independently, using parameters shared across the whole image. They use fewer parameters than fully connected layers, exploit the spatial relationships between nearby pixels, and don’t have to re-learn the interpretation of the pixels at every position. A network predominantly consisting of convolutional layers is known as a convolutional neural network or CNN.

## 10.1 Invariance and equivariance

> ![10.2](/contents/understanding-deep-learning/10.2.png)
> 
> Figure 10.2 1D convolution with kernel size three. Each output zi is a weighted sum of the nearest three inputs xi−1, xi, and xi+1, where the weights are ω = [ω1, ω2, ω3]. a) Output z2 is computed as z2 = ω1x1 + ω2x2 + ω3x3. b) Output z3 is computed as z3 = ω1x2 + ω2x3 + ω3x4. c) At position z1, the kernel extends beyond the first input x1. This can be handled by zero-padding, in which we assume values outside the input are zero. The final output is treated similarly. d) Alternatively, we could only compute outputs where the kernel fits within the input range (“valid” convolution); now, the output will be smaller than the input.

## 10.2 Convolutional networks for 1D inputs

### 10.2.1 1D convolution operation

> ![10.3](/contents/understanding-deep-learning/10.3.png)
> 
> Figure 10.3 Stride, kernel size, and dilation. a) With a stride of two, we evaluate the kernel at every other position, so the first output z1 is computed from a weighted sum centered at x1, and b) the second output z2 is computed from a weighted sum centered at x3 and so on. c) The kernel size can also be changed. With a kernel size of five, we take a weighted sum of the nearest five inputs. d) In dilated or atrous convolution (from the French “à trous” – with holes), we intersperse zeros in the weight vector to allow us to combine information over a large area using fewer weights.

### 10.2.5 Channels

> ![10.5](/contents/understanding-deep-learning/10.5.png)
>
> Figure 10.5 Channels. Typically, multiple convolutions are applied to the input x and stored in channels. a) A convolution is applied to create hidden units h1 to h6, which form the first channel. b) A second convolution operation is applied to create hidden units h7 to h12, which form the second channel. The channels are stored in a 2D array H1 that contains all the hidden units in the first hidden layer. c) If we add a further convolutional layer, there are now two channels at each input position. Here, the 1D convolution defines a weighted sum over both input channels at the three closest positions to create each new output channel.

### 10.2.7 Example: MNIST-1D

> ![10.6](/contents/understanding-deep-learning/10.6.png)
>
> Figure 10.6 Receptive fields for network with kernel width of three. a) An input with eleven dimensions feeds into a hidden layer with three channels and convolution kernel of size three. The pre-activations of the three highlighted hidden units in the first hidden layer H1 are different weighted sums of the nearest three inputs, so the receptive field in H1 has size three. b) The pre-activations of the four highlighted hidden units in layer H2 each take a weighted sum of the three channels in layer H1 at each of the three nearest positions. Each hidden unit in layer H1 weights the nearest three input positions. Hence, hidden units in H2 have a receptive field size of five. c) The hidden units in the third layer (kernel size three, stride two) increases the receptive field size to seven. d) By the time we add a fourth layer, the receptive field of the hidden units at position three have a receptive field that covers the entire input.

## 10.3 Convolutional networks for 2D inputs

> ![10.9](/contents/understanding-deep-learning/10.9.png)
>
> Figure 10.9 2D convolutional layer. Each output hij computes a weighted sum of the 3×3 nearest inputs, adds a bias, and passes the result through an activation function. a) Here, the output h23 (shaded output) is a weighted sum of the nine positions from x12 to x34 (shaded inputs). b) Different outputs are computed by translating the kernel across the image grid in two dimensions. c–d) With zero-padding, positions beyond the image’s edge are considered to be zero.

## 10.4 Downsampling and upsampling

### 10.4.1 Downsampling

> ![10.10](/contents/understanding-deep-learning/10.10.png)
>
> Figure 10.10 2D convolution applied to an image. The image is treated as a 2D input with three channels corresponding to the red, green, and blue components. With a 3×3 kernel, each pre-activation in the first hidden layer is computed by pointwise multiplying the 3×3×3 kernel weights with the 3×3 RGB image patch centered at the same position, summing, and adding the bias. To calculate all the pre-activations in the hidden layer, we “slide” the kernel over the image in both horizontal and vertical directions. The output is a 2D layer of hidden units. To create multiple output channels, we would repeat this process with multiple kernels, resulting in a 3D tensor of hidden units at hidden layer H1.

### 10.4.2 Upsampling

> ![10.11](/contents/understanding-deep-learning/10.11.png)
>
> Figure 10.11 Methods for scaling down representation size (downsampling). a) Sub-sampling. The original 4×4 representation (left) is reduced to size 2×2 (right) by retaining every other input. Colors on the left indicate which inputs contribute to the outputs on the right. This is effectively what happens with a kernel of stride two, except that the intermediate values are never computed. b) Max pooling. Each output comprises the maximum value of the corresponding 2×2 block. c) Mean pooling. Each output is the mean of the values in the 2×2 block.

> ![10.12](/contents/understanding-deep-learning/10.12.png)
> 
> Figure 10.12 Methods for scaling up representation size (upsampling). a) The simplest way to double the size of a 2D layer is to duplicate each input four times. b) In networks where we have previously used a max pooling operation (figure 10.11b), we can redistribute the values to the same positions they originally came from (i.e., where the maxima were). This is known as max unpooling. c) A third option is bilinear interpolation between the input values.

## 10.5 Applications

### 10.5.2 Object detection

> ![10.18](/contents/understanding-deep-learning/10.18.png)
>
> Figure 10.18 YOLO object detection. a) The input image is reshaped to 448×448 and divided into a regular 7×7 grid. b) The system predicts the most likely class at each grid cell. c) It also predicts two bounding boxes per cell, and a confidence value (represented by thickness of line). d) During inference, the most likely bounding boxes are retained, and boxes with lower confidence values that belong to the same object are suppressed. Adapted from Redmon et al. (2016).

## 10.6 Summary

> In convolutional layers, each hidden unit is computed by taking a weighted sum of the nearby inputs, adding a bias, and applying an activation function. The weights and the bias are the same at every spatial position, so there are far fewer parameters than in a fully connected network, and the number of parameters doesn’t increase with the input image size. To ensure that information is not lost, this operation is repeated with different weights and biases to create multiple channels at each spatial position.

> Typical convolutional networks consist of convolutional layers interspersed with layers that downsample by a factor of two. As the network progresses, the spatial dimensions usually decrease by factors of two, and the number of channels increases by factors of two. At the end of the network, there are typically one or more fully connected layers that integrate information from across the entire input and create the desired output. If the output is an image, a mirrored “decoder” upsamples back to the original size.

> The translational equivariance of convolutional layers imposes a useful inductive bias that increases performance for image-based tasks relative to fully connected networks. We described image classification, object detection, and semantic segmentation networks. Image classification performance was shown to improve as the network became deeper. However, subsequent experiments showed that increasing the network depth indefinitely doesn’t continue to help; after a certain depth, the system becomes diﬀicult to train. This is the motivation for residual connections, which are the topic of the next chapter.

> Convolution in 1D and 3D: 
> 
> Convolutional networks are usually applied to images but have also been applied to 1D data in applications that include speech recognition (Abdel-Hamid et al., 2012), sentence classification (Zhang et al., 2015; Conneau et al., 2017), electrocardiogram classification (Kiranyaz et al., 2015), and bearing fault diagnosis (Eren et al., 2019). A survey of 1D convolutional networks can be found in Kiranyaz et al. (2021). Convolutional networks have also been applied to 3D data, including video (Ji et al., 2012; Saha et al., 2016; Tran et al., 2015) and volumetric measurements (Wu et al., 2015b; Maturana & Scherer, 2015).

> For example, Bau et al. (2017) showed that earlier layers correlate more with texture and color and later layers with the object type. However, it is fair to say that fully understanding the processing of networks containing millions of parameters is currently not possible.

# Chapter 11 Residual networks

## 11.4 Batch normalization

> ![11.6](/contents/understanding-deep-learning/11.6.png)
>
> Figure 11.6 Variance in residual networks. a) He initialization ensures that the expected variance remains unchanged after a linear plus ReLU layer fk. Unfortunately, in residual networks, the input of each block is added back to the output, so the variance doubles at each layer (gray numbers indicate variance) and grows exponentially. b) One approach would be to rescale the signal by 1/√2 between each residual block. c) A second method uses batch normalization (BN) as the first step in the residual block and initializes the associated offset δ to zero and scale γ to one. This transforms the input to each layer to have unit variance, and with He initialization, the output variance will also be one. Now the variance increases linearly with the number of residual blocks. A side-effect is that, at initialization, later network layers are dominated by the residual connection and are hence close to computing the identity.

## 11.5 Common residual architectures

### 11.5.1 ResNet

> Residual blocks were first used in convolutional networks for image classification. The resulting networks are known as residual networks, or ResNets for short.

### 11.5.2 DenseNet

> Residual blocks receive the output from the previous layer, modify it by passing it through some network layers, and add it back to the original input.

> ![11.7](/contents/understanding-deep-learning/11.7.png)
>
> Figure 11.7 ResNet blocks. a) A standard block in the ResNet architecture contains a batch normalization operation, followed by an activation function, and a 3×3 convolutional layer. Then, this sequence is repeated. b). A bottleneck ResNet block still integrates information over a 3×3 region but uses fewer parameters. It contains three convolutions. The first 1×1 convolution reduces the number of channels. The second 3×3 convolution is applied to the smaller representation. A final 1×1 convolution increases the number of channels again so that it can be added back to the input.

> ![11.8](/contents/understanding-deep-learning/11.8.png)
>
> Figure 11.8 ResNet-200 model. A standard 7×7 convolutional layer with stride two is applied, followed by a MaxPool operation. A series of bottleneck residual blocks follow (number in brackets is channels after first 1×1 convolution), with periodic downsampling and accompanying increases in the number of channels. The network concludes with average pooling across all spatial positions and a fully connected layer that maps to pre-softmax activations.

> ![11.9](/contents/understanding-deep-learning/11.9.png)
>
> Figure 11.9 DenseNet. This architecture uses residual connections to concatenate the outputs of earlier layers to later ones. Here, the three-channel input image is processed to form a 32-channel representation. The input image is concatenated to this to give a total of 35 channels. This combined representation is processed to create another 32-channel representation, and both earlier representations are concatenated to this to create a total of 67 channels and so on.

### 11.5.3 U-Nets and hourglass networks

> ![11.10](/contents/understanding-deep-learning/11.10.png)
>
> Figure 11.10 U-Net for segmenting HeLa cells. The U-Net has an encoder-decoder structure, in which the representation is downsampled (orange blocks) and then re-upsampled (blue blocks). The encoder uses regular convolutions, and the decoder uses transposed convolutions. Residual connections append the last representation at each scale in the encoder to the first representation at the same scale in the decoder (orange arrows). The original U-Net used “valid” convolutions, so the size decreased slightly with each layer, even without downsampling. Hence, the representations from the encoder were cropped (dashed squares) before appending to the decoder. Adapted from Ronneberger et al. (2015).

> ![11.11](/contents/understanding-deep-learning/11.11.png)
>
> Figure 11.11 Segmentation using U-Net in 3D. a) Three slices through a 3D volume of mouse cortex taken by scanning electron microscope. b) A single U-Net is used to classify voxels as being inside or outside neurites. Connected regions are identified with different colors. c) For a better result, an ensemble of five U-Nets is trained, and a voxel is only classified as belonging to the cell if all five networks agree. Adapted from Falk et al. (2019).

## 11.6 Why do nets with residual connections perform so well?

> Residual networks allow much deeper networks to be trained; it’s possible to extend the ResNet architecture to 1000 layers and still train effectively.

## 11.7 Summary

> ![11.12](/contents/understanding-deep-learning/11.12.png)
>
> Figure 11.12 Stacked hourglass networks for pose estimation. a) The network input is an image containing a person, and the output is a set of heatmaps, with one heatmap for each joint. This is formulated as a regression problem where the targets are heatmap images with small, highlighted regions at the ground-truth joint positions. The peak of the estimated heatmap is used to establish each final joint position. b) The architecture consists of initial convolutional and residual layers followed by a series of hourglass blocks. c) Each hourglass block consists of an encoder-decoder network similar to the U-Net except that the convolutions use zero-padding, some further processing is done in the residual links, and these links add this processed representation rather than concatenate it. Each blue cuboid is itself a bottleneck residual block (figure 11.7b). Adapted from Newell et al. (2016).

> ![11.13](/contents/understanding-deep-learning/11.13.png)
>
> Figure 11.13 Visualizing neural network loss surfaces. Each plot shows the loss surface in two random directions in parameter space around the minimum found by SGD for an image classification task on the CIFAR-10 dataset. These directions are normalized to facilitate side-by-side comparison. a) Residual net with 56 layers. b) Results from the same network without skip connections. The surface is smoother with the skip connections. This facilitates learning and makes the final network performance more robust to minor errors in the parameters, so it will likely generalize better. Adapted from Li et al. (2018b).

> ![11.14](/contents/understanding-deep-learning/11.14.png)
>
> Figure 11.14 Normalization schemes. BatchNorm modifies each channel separately but adjusts each batch member in the same way based on statistics gathered across the batch and spatial position. Ghost BatchNorm computes these statistics from only part of the batch to make them more variable. LayerNorm computes statistics for each batch member separately, based on statistics gathered across the channels and spatial position. It retains a separate learned scaling factor for each channel. GroupNorm normalizes within each group of channels and also retains a separate scale and offset parameter for each channel. InstanceNorm normalizes within each channel separately, computing the statistics only across spatial position. Adapted from Wu & He (2018).

# Chapter 12 Transformers

## 12.1 Processing text data

> A more realistically sized body of text might have hundreds or even thousands of words, so fully connected neural networks are impractical.

> ... each input (one or more sentences) is of a different length; hence, it’s not even obvious how to apply a fully connected network. These observations suggest that the network should share parameters across words at different input positions, similarly to how convolutional networks share parameters across different image positions.

> In the parlance of transformers, the former word should pay attention to the latter.

## 12.2 Dot-product self-attention

> The previous section argued that a model for processing text will (i) use parameter sharing to cope with long input passages of differing lengths and (ii) contain connections between word representations that depend on the words themselves. The transformer acquires both properties by using dot-product self-attention.

> ![12.1](/contents/understanding-deep-learning/12.1.png)
>
> Figure 12.1 Self-attention as routing. The self-attention mechanism takes N inputs x1,...,xN ∈ RD (here N = 3 and D = 4) and processes each separately to compute N value vectors. The nth output san [x1 , . . . xN ] (written as san [x• ] for short) is then computed as a weighted sum of the N value vectors, where the weights are positive and sum to one. a) Output sa1[x•] is computed as a[x1,x1] = 0.1 times the first value vector, a[x2,x1] = 0.3 times the second value vector, and a[x3,x1] = 0.6 times the third value vector. b) Output sa2[x•] is computed in the same way, but this time with weights of 0.5, 0.2, and 0.3. c) The weighting for output sa3[x•] is different again. Each output can hence be thought of as a different routing of the N values.

### 12.2.2 Computing attention weights

> To compute the attention, we apply two more linear transformations to the inputs:
>
> q<sub>n</sub> = β<sub>q</sub> + Ω<sub>q</sub>x<sub>n</sub>
>
> k<sub>m</sub> = β<sub>k</sub> + Ω<sub>k</sub>x<sub>m</sub>
>
> where {qn} and {km} are termed queries and keys, respectively.

> ![12.3](/contents/understanding-deep-learning/12.3.png)
>
> Figure 12.3 Computing attention weights. a) Query vectors qn = βq + Ωqxn and key vectors kn = βk + Ωkxn are computed for each input xn. b) The dot products between each query and the three keys are passed through a softmax function to form non-negative attentions that sum to one. c) These route the value vectors (figure 12.1) via the sparse matrix from figure 12.2c.

### 12.2.3 Self-attention summary

> ![12.4](/contents/understanding-deep-learning/12.4.png)
>
> Figure 12.4 Self-attention in matrix form. Self-attention can be implemented eﬀiciently if we store the N input vectors xn in the columns of the D×N matrix X. The input X is operated on separately by the query matrix Q, key matrix K, and value matrix V. The dot products are then computed using matrix multiplication, and a softmax operation is applied independently to each column of the resulting matrix to calculate the attentions. Finally, the values are post-multiplied by the attentions to create an output of the same size as the input.

## 12.3 Extensions to dot-product self-attention

### 12.3.3 Multiple heads

> Multiple self-attention mechanisms are usually applied in parallel, and this is known as multi-head self-attention.

> ![12.6](/contents/understanding-deep-learning/12.6.png)
>
> Figure 12.6 Multi-head self-attention. Self-attention occurs in parallel across multiple “heads.” Each has its own queries, keys, and values. Here two heads are depicted, in the cyan and orange boxes, respectively. The outputs are vertically concatenated, and another linear transformation Ωc is used to recombine them.

## 12.4 Transformer layers

> ![12.7](/contents/understanding-deep-learning/12.7.png)
>
> Figure 12.7 Transformer layer. The input consists of a D × N matrix containing the D-dimensional word embeddings for each of the N input tokens. The output is a matrix of the same size. The transformer layer consists of a series of operations. First, there is a multi-head attention block, allowing the word embeddings to interact with one another. This forms the processing of a residual block, so the inputs are added back to the output. Second, a LayerNorm operation is applied. Third, there is a second residual layer where the same fully connected neural network is applied separately to each of the N word representations (columns). Finally, LayerNorm is applied again.

## 12.5 Transformers for natural language processing

> ![12.8](/contents/understanding-deep-learning/12.8.png)
>
> Figure 12.8 Sub-word tokenization. a) A passage of text from a nursery rhyme. The tokens are initially just the characters and whitespace (represented by an underscore), and their frequencies are displayed in the table. b) At each iteration, the sub-word tokenizer looks for the most commonly occurring adjacent pair of tokens (in this case, se) and merges them. This creates a new token and decreases the counts for the original tokens s and e. c) At the second iteration, the algorithm merges e and the whitespace character_. Note that the last character of the first token to be merged cannot be whitespace, which prevents merging across words. d) After 22 iterations, the tokens consist of a mix of letters, word fragments, and commonly occurring words. e) If we continue this process indefinitely, the tokens eventually represent the full words. f) Over time, the number of tokens increases as we add word fragments to the letters and then decreases again as we merge these fragments. In a real situation, there would be a very large number of words, and the algorithm would terminate when the vocabulary size (number of tokens) reached a predetermined value. Punctuation and capital letters would also be treated as separate input characters.

### 12.5.1 Tokenization

> In practice, a compromise between letters and full words is used, and the final vocabulary includes both common words and word fragments from which larger and less frequent words can be composed. The vocabulary is computed using a sub-word tokenizer such as byte pair encoding (figure 12.8) that greedily merges commonly occurring sub-strings based on their frequency.

### 12.5.2 Embeddings

> A typical embedding size D is 1024, and a typical total vocabulary size |V| is 30,000, so even before the main network, there are many parameters in Ωe to learn.

### 12.5.3 Transformer model

> Finally, the embedding matrix X representing the text is passed through a series of K transformer layers, called a transformer model. There are three types of transformer models. An encoder transforms the text embeddings into a representation that can support a variety of tasks. A decoder predicts the next token to continue the input text. Encoder-decoders are used in sequence-to-sequence tasks, where one text string is converted into another (e.g., machine translation).

> ![12.9](/contents/understanding-deep-learning/12.9.png)
>
> Figure 12.9 The input embedding matrix X ∈ RD×N contains N embeddings of length D and is created by multiplying a matrix Ωe containing the embeddings for the entire vocabulary with a matrix containing one-hot vectors in its columns that correspond to the word or sub-word indices. The vocabulary matrix Ωe is considered a parameter of the model and is learned along with the other parameters. Note that the two embeddings for the word an in X are the same.

## 12.6 Encoder model example: BERT

> BERT is an encoder model that uses a vocabulary of 30,000 tokens. Input tokens are converted to 1024-dimensional word embeddings and passed through 24 transformer layers. Each contains a self-attention mechanism with 16 heads. The queries, keys, and values for each head are of dimension 64 (i.e., the matrices Ωvh, Ωqh, Ωkh are 1024 × 64). The dimension of the single hidden layer in the fully connected networks is 4096. The total number of parameters is ∼ 340 million.

> ![12.10](/contents/understanding-deep-learning/12.10.png)
> 
> Figure 12.10 Pre-training for BERT-like encoder. The input tokens (and a special <cls> token denoting the start of the sequence) are converted to word embeddings. Here, these are represented as rows rather than columns, so the box labeled “word embeddings” is XT . These embeddings are passed through a series of transformer layers (orange connections indicate that every token attends to every other token in these layers) to create a set of output embeddings. A small fraction of the input tokens are randomly replaced with a generic <mask> token. In pre-training, the goal is to predict the missing word from the associated output embedding. As such, the output embeddings are passed through a softmax function, and the multiclass classification loss (section 5.24) is used. This task has the advantage that it uses both the left and right context to predict the missing word but has the disadvantage that it does not make eﬀicient use of data; here, seven tokens need to be processed to add two terms to the loss function.

### 12.6.1 Pre-training

> ![12.11](/contents/understanding-deep-learning/12.11.png)
>
> Figure 12.11 After pre-training, the encoder is fine-tuned using manually labeled data to solve a particular task. Usually, a linear transformation or a multi-layer perceptron (MLP) is appended to the encoder to produce whatever output is required. a) Example text classification task. In this sentiment classification task, the <cls> token embedding is used to predict the probability that the review is positive. b) Example word classification task. In this named entity recognition problem, the embedding for each word is used to predict whether the word corresponds to a person, place, or organization, or is not an entity.

## 12.7 Decoder model example: GPT3

> The encoder aimed to build a representation of the text that could be finetuned to solve a variety of more specific NLP tasks. Conversely, the decoder has one purpose: to generate the next token in a sequence.

### 12.7.1 Language modeling

> The probability of the full sentence is:
> ```text
> Pr(It takes great courage to let yourself appear weak) =
>     Pr(It) × Pr(takes|It) × Pr(great|It takes) × Pr(courage|It takes great) ×
>     Pr(to|It takes great courage) × Pr(let|It takes great courage to) ×
>     Pr(yourself|It takes great courage to let) ×
>     Pr(appear|It takes great courage to let yourself) ×
>     Pr(weak|It takes great courage to let yourself appear).
> ```

### 12.7.3 Generating text from a decoder

> ![12.12](/contents/understanding-deep-learning/12.12.png)
>
> Figure 12.12 Training GPT3-type decoder network. The tokens are mapped to word embeddings with a special <start> token at the beginning of the sequence. The embeddings are passed through a series of transformer layers that use masked self-attention. Here, each position in the sentence can only attend to its own embedding and those of tokens earlier in the sequence (orange connections). The goal at each position is to maximize the probability of the following ground truth token in the sequence. In other words, at position one, we want to maximize the probability of the token It; at position two, we want to maximize the probability of the token takes; and so on. Masked self-attention ensures the system cannot cheat by looking at subsequent inputs. The autoregressive task has the advantage of making eﬀicient use of the data since every word contributes a term to the loss function. However, it only exploits the left context of each word.

### 12.7.4 GPT3 and few-shot learning

> Large language models like GPT3 apply these ideas on a massive scale. In GPT3, the sequence lengths are 2048 tokens long, and the total batch size is 3.2 million tokens. There are 96 transformer layers (some of which implement a sparse version of attention), each processing a word embedding of size 12288. There are 96 heads in the self-attention layers, and the value, query, and key dimension is 128. It is trained with 300 billion tokens and contains 175 billion parameters.

> ![12.13](/contents/understanding-deep-learning/12.13.png)
>
> Figure 12.13 Encoder-decoder architecture. Two sentences are passed to the system with the goal of translating the first into the second. a) The first sentence is passed through a standard encoder. b) The second sentence is passed through a decoder that uses masked self-attention but also attends to the output embeddings of the encoder using cross-attention (orange rectangle). The loss function is the same as for the decoder model; we want to maximize the probability of the next word in the output sequence.

## 12.8 Encoder-decoder model example: machine translation

> ![12.14](/contents/understanding-deep-learning/12.14.png)
>
> Figure 12.14 Cross-attention. The flow of computation is the same as in standard self-attention. However, the queries are calculated from the decoder embeddings Xdec, and the keys and values from the encoder embeddings Xenc. In the context of translation, the encoder contains information about the source language, and the decoder contains information about the target language statistics.

## 12.9 Transformers for long sequences

> ![12.15](/contents/understanding-deep-learning/12.15.png)
>
> Figure 12.15 Interaction matrices for self-attention. a) In an encoder, every token interacts with every other token, and computation expands quadratically with the number of tokens. b) In a decoder, each token only interacts with the previous tokens, but complexity is still quadratic. c) Complexity can be reduced by using a convolutional structure (encoder case). d) Convolutional structure for decoder case. e–f) Convolutional structure with dilation rate of two and three (decoder case). g) Another strategy is to allow selected tokens to interact with all the other tokens (encoder case) or all the previous tokens (decoder case pictured). h) Alternatively, global tokens can be introduced (left two columns and top two rows). These interact with all of the tokens as well as with each other.

## 12.10 Transformers for images

### 12.10.3 Multi-scale vision transformers

> ![12.17](/contents/understanding-deep-learning/12.17.png)
>
> Figure 12.17 Vision transformer. The Vision Transformer (ViT) breaks the image into a grid of patches (16×16 in the original implementation). Each of these is projected via a learned linear transformation to become a patch embedding. These patch embeddings are fed into a transformer encoder network, and the <cls> token is used to predict the class probabilities.

> ![12.18](/contents/understanding-deep-learning/12.18.png)
>
> Figure 12.18 Shifted window (SWin) transformer (Liu et al., 2021c). a) Original image. b) The SWin transformer breaks the image into a grid of windows and each of these windows into a sub-grid of patches. The transformer network applies self-attention to the patches within each window independently. c) Each alternate layer shifts the windows so that the subsets of patches that interact with one another change, and information can propagate across the whole image. d) After several layers, the 2 × 2 blocks of patch representations are concatenated to increase the effective patch (and window) size. e) Alternate layers use shifted windows at this new lower resolution. f) Eventually, the resolution is such that there is just a single window, and the patches span the entire image.

## 12.11 Summary

> ![12.19](/contents/understanding-deep-learning/12.19.png)
>
> Figure 12.19 Recurrent neural networks (RNNs). The word embeddings are passed sequentially through a series of identical neural networks. Each network has two outputs; one is the output embedding, and the other (orange arrows) feeds back into the next neural network, along with the next word embedding. Each output embedding contains information about the word itself and its context in the preceding sentence fragment. In principle, the final output contains information about the entire sentence and could be used to support classification tasks similarly to the <cls> token in a transformer encoder model. However, RNNs sometimes gradually “forget” about tokens that are further back in time.

> One of the problems with RNNs is that they can forget information that is further back in the sequence. More sophisticated versions of this architecture, such as long short-term memory networks or LSTMs (Hochreiter & Schmidhuber, 1997b) and gated recurrent units or GRUs (Cho et al., 2014; Chung et al., 2014) partially addressed this problem.

> Extending transformers to longer sequences: 
> 
> The complexity of the self-attention mechanism increases quadratically with the sequence length. Some tasks like summarization or question answering may require long inputs, so this quadratic dependence limits performance. Three lines of work have attempted to address this problem. The first decreases the size of the attention matrix, the second makes the attention sparse, and the third modifies the attention mechanism to make it more eﬀicient.

# Chapter 13 Graph neural networks

## 13.1 What is a graph?

### 13.1.1 Types of graphs

> ![13.3](/contents/understanding-deep-learning/13.3.png)
>
> Figure 13.3 Graph representation. a) Example graph with six nodes and seven edges. Each node has an associated embedding of length five (brown vectors). Each edge has an associated embedding of length four (blue vectors). This graph can be represented by three matrices. b) The adjacency matrix is a binary matrix where element (m,n) is set to one if node m connects to node n. c) The node data matrix X contains the concatenated node embeddings. d) The edge data matrix E contains the edge embeddings.

## 13.2 Graph representation

> ![13.4](/contents/understanding-deep-learning/13.4.png)
>
> Figure 13.4 Properties of the adjacency matrix. a) Example graph. b) Position (m, n) of the adjacency matrix A contains the number of walks of length one from node m to node n. c) Position (m, n) of the squared adjacency matrix A2 contains the number of walks of length two from node n to node m. d) One hot vector representing node six, which was highlighted in panel (a). e) When we pre-multiply this vector by A, the result contains the number of walks of length one from node six to each node; we can reach nodes five, seven, and eight in one move. f) When we pre-multiply this vector by A2, the resulting vector contains the number of walks of length two from node six to each node; we can reach nodes two, three, four, five, and eight in two moves, and we can return to the original node in three different ways (via nodes five, seven, and eight).

## 13.3 Graph neural networks, tasks, and loss functions

### 13.3.1 Tasks and loss functions

> ![13.6](/contents/understanding-deep-learning/13.6.png)
>
> Figure 13.6 Common tasks for graphs. In each case, the input is a graph represented by its adjacency matrix and node embeddings. The graph neural network processes the node embeddings by passing them through a series of layers. The node embeddings at the last layer contain information about both the node and its context in the graph. a) Graph classification. The node embeddings are combined (e.g., by averaging) and then mapped to a fixed-size vector that is passed through a softmax function to produce class probabilities. b) Node classification. Each node embedding is used individually as the basis for classification (cyan and orange colors represent assigned node classes). c) Edge prediction. Node embeddings adjacent to the edge are combined (e.g., by taking the dot product) to compute a single number that is mapped via a sigmoid function to produce a probability that a missing edge should be present.

## 13.4 Graph convolutional networks

### 13.4.2 Parameter sharing

> ![13.7](/contents/understanding-deep-learning/13.7.png)
>
> Figure 13.7 Simple Graph CNN layer. a) Input graph consists of structure (embodied in graph adjacency matrix A, not shown) and node embeddings (stored in columns of X). b) Each node in the first hidden layer is updated by (i) aggregating the neighboring nodes to form a single vector, (ii) applying a linear transformation Ω0 to the aggregated nodes, (iii) applying the same linear transformation Ω0 to the original node, (iv) adding these together with a bias β0, and finally (v) applying a nonlinear activation function a[•] like a ReLU. c) This process is repeated at subsequent layers (but with different parameters for each layer) until we produce the final embeddings at the end of the network.

## 13.5 Example: graph classification

### 13.5.1 Training with batches

> ![13.8](/contents/understanding-deep-learning/13.8.png)
>
> Figure 13.8 Inductive vs. transductive problems. a) Node classification task in the inductive setting. We are given a set of I training graphs, where the node labels (orange and cyan colors) are known. After training, we are given a test graph and must assign labels to each node. b) Node classification in the transductive setting. There is one large graph in which some nodes have labels (orange and cyan colors), and others are unknown. We train the model to predict the known labels correctly and then examine the predictions at the unknown nodes.

## 13.7 Example: node classification

### 13.7.1 Choosing batches

> ![13.9](/contents/understanding-deep-learning/13.9.png)
>
> Figure 13.9 Receptive fields in graph neural networks. Consider the orange node in hidden layer two (right). This receives input from the nodes in the 1-hop neighborhood in hidden layer one (shaded region in center). These nodes in hidden layer one receive inputs from their neighbors in turn, and the orange node in layer two receives inputs from all the input nodes in the 2-hop neighborhood (shaded area on left). The region of the graph that contributes to a given node is equivalent to the notion of a receptive field in convolutional neural networks.

## 13.8 Layers for graph convolutional networks

### 13.8.6 Aggregation by attention

> ![13.12](/contents/understanding-deep-learning/13.12.png)
>
> Figure 13.12 Comparison of graph convolutional network, dot product attention, and graph attention network. In each case, the mechanism maps N embeddings of size D stored in a D×N matrix X to an output of the same size. a) The graph convolutional network applies a linear transformation X′ = ΩX to the data matrix. It then computes a weighted sum of the transformed data, where the weighting is based on the adjacency matrix. A bias β is added, and the result is passed through an activation function. b) The outputs of the self-attention mechanism are also weighted sums of the transformed inputs, but this time the weights depend on the data itself via the attention matrix. c) The graph attention network combines both of these mechanisms; the weights are both computed from the data and based on the adjacency matrix.

## 13.9 Edge graphs

> ![13.13](/contents/understanding-deep-learning/13.13.png)
>
> Figure 13.13 Edge graph. a) Graph with six nodes. b) To create the edge graph, we assign one node for each original edge (cyan circles), and c) connect the new nodes if the edges they represent connect to the same node in the original graph.

# Chapter 14 Unsupervised learning

## 14.1 Taxonomy of unsupervised learning models

> ![14.1](/contents/understanding-deep-learning/14.1.png)
>
> Figure 14.1 Taxonomy of unsupervised learning models. Unsupervised learning refers to any model trained on datasets without labels. Generative models can synthesize (generate) new examples with similar statistics to the training data. A subset of these are probabilistic and define a distribution over the data. We draw samples from this distribution to generate new examples. Latent variable models define a mapping between an underlying explanatory (latent) variable and the data. They may fall into any of the above categories.

## 14.2 What makes a good generative model?

> Note that not all probabilistic generative models rely on latent variables. The transformer decoder (section 12.7) was learned without labels, can generate new examples, and can assign a probability to these examples but is based on an autoregressive formulation (equation 12.15).

> ![14.2](/contents/understanding-deep-learning/14.2.png)
>
> Figure 14.2 Fitting generative models a) Generative adversarial models provide a mechanism for generating samples (orange points). As training proceeds (left to right), the loss function encourages these samples to become progressively less distinguishable from real examples (cyan points). b) Probabilistic models (including variational autoencoders, normalizing flows, and diffusion models) learn a probability distribution over the training data. As training proceeds (left to right), the likelihood of the real examples increases under this distribution, which can be used to draw new samples and assess the probability of new data points.

# Chapter 15 Generative Adversarial Networks

## 15.2 Improving stability

### 15.2.6 Wasserstein GAN loss function

> ![15.9](/contents/understanding-deep-learning/15.9.png)
>
> Figure 15.9 Progressive growing. a) The generator is initially trained to create very small (4×4) images, and the discriminator to identify if these images are synthesized or downsampled real images. b) After training at this low-resolution terminates, subsequent layers are added to the generator to generate (8×8) images. Similar layers are added to the discriminator to downsample back again. c) This process continues to create (16×16) images and so on. In this way, a GAN that produces very realistic high-resolution images can be trained. d) Images of increasing resolution generated at different stages from the same latent variable. Adapted from Wolf (2021), using method of Karras et al. (2018).

## 15.4 Conditional generation

### 15.4.2 Auxiliary classifier GAN

> ![15.13](/contents/understanding-deep-learning/15.13.png)
>
> Figure 15.13 Conditional generation. a) The generator of the conditional GAN also receives an attribute vector c describing some aspect of the image. As usual, the discriminator receives either a real example or a generated sample, but now it also receives the attribute vector; this encourages the samples both to be realistic and compatible with the attribute. b) The generator of the auxiliary classifier GAN (ACGAN) takes a discrete attribute variable. The discriminator must both (i) determine if its input is real or synthetic and (ii) identify the class correctly. c) The InfoGAN splits the latent variable into noise z and unspecified random attributes c. The discriminator must distinguish if its input is real and also reconstruct these attributes. In practice, this means that the variables c correspond to salient aspects of the data with real-world interpretations (i.e., the latent space is disentangled).

## 15.5 Image translation

### 15.5.3 CycleGAN

> ![15.16](/contents/understanding-deep-learning/15.16.png)
>
> Figure 15.16 Pix2Pix model. a) The model translates an input image to a prediction in a different style using a U-Net (see figure 11.10). In this case, it maps a grayscale image to a plausibly colored version. The U-Net is trained with two losses. First, the content loss encourages the output image to have a similar structure to the input image. Second, the adversarial loss encourages the grayscale/color image pair to be indistinguishable from a real pair in each local region of these images. This framework can be adapted to many tasks, including b) translating maps to satellite imagery, c) converting sketches of bags to photorealistic examples, d) colorization, and e) converting label maps to photorealistic building facades. Adapted from Isola et al. (2017).

> ![15.17](/contents/understanding-deep-learning/15.17.png)
>
> Figure 15.17 Super-resolution generative adversarial network (SRGAN). a) A convolutional network with residual connections is trained to increase the resolution of images by a factor of four. The model has losses that encourage the content to be close to the true high-resolution image. However, it also includes an adversarial loss, which penalizes results that can be distinguished from real high-resolution images. b) Upsampled image using bicubic interpolation. c) Upsampled image using SRGAN. d) Upsampled image using bicubic interpolation. e) Upsampled image using SRGAN. Adapted from Ledig et al. (2017).

## 15.6 StyleGAN

> ![15.18](/contents/understanding-deep-learning/15.18.png)
>
> Figure 15.18 CycleGAN. Two models are trained simultaneously. The first c′ = g[cj,θ] translates from an image c in the first style (horse) to an image c′ in the second style (zebra). The second model c = g′ [c′ , θ] learns the opposite mapping. The cycle consistency loss penalizes both models if they cannot successfully convert an image to the other domain and back to the original. In addition, two adversarial losses encourage the translated images to look like realistic examples of the target domain (shown here for zebra only). Two content losses encourage the details and layout of the images before and after each mapping to be similar (i.e., the zebra is in the same position and pose that the horse was and against the same background and vice versa). Adapted from Zhu et al. (2017).

> ![15.19](/contents/understanding-deep-learning/15.19.png)
>
> Figure 15.19 StyleGAN. The main pipeline (center row) starts with a constant learned representation (gray box). This is passed through a series of convolutional layers and gradually upsampled to create the output. Noise (top row) is added at different scales by periodically adding Gaussian variables z• with per-channel scaling ψ•. The Gaussian style variable z is passed through a fully connected network to create intermediate variable w (bottom row). This is used to set the mean and variance of each channel at various points in the pipeline.

# Chapter 17 Variational autoencoders

## 17.2 Nonlinear latent variable model

> ![17.1](/contents/understanding-deep-learning/17.1.png)
> 
> Figure 17.1 Mixture of Gaussians (MoG). a) The MoG describes a complex probability distribution (cyan curve) as a weighted sum of Gaussian components (dashed curves). b) This sum is the marginalization of the joint density Pr(x,z) between the continuous observed data x and a discrete latent variable z.

# Chapter 18 Diffusion models

## 18.1 Overview

> ![18.1](/contents/understanding-deep-learning/18.1.png)
>
> Figure 18.1 Diffusion models. The encoder (forward, or diffusion process) maps the input x through a series of latent variables z1 . . . zT . This process is prespecified and gradually mixes the data with noise until only noise remains. The decoder (reverse process) is learned and passes the data back through the latent variables, removing noise at each stage. After training, new examples are generated by sampling noise vectors zT and passing them through the decoder.

## 18.7 Summary

> Diffusion models map the data examples through a series of latent variables by repeatedly blending the current representation with random noise. After suﬀicient steps, the representation becomes indistinguishable from white noise. Since these steps are small, the reverse denoising process at each step can be approximated with a normal distribution and predicted by a deep learning model. The loss function is based on the evidence lower bound (ELBO) and ultimately results in a simple least-squares formulation.

> For image generation, each denoising step is implemented using a U-Net, so sampling is slow compared to other generative models. To improve generation speed, it’s possible to change the diffusion model to a deterministic formulation, and here sampling with fewer steps works well. Several methods have been proposed to condition generation on class information, images, and text information. Combining these methods produces impressive text-to-image synthesis results.

# Chapter 19 Reinforcement learning

> Reinforcement learning (RL) is a sequential decision-making framework in which agents learn to perform actions in an environment with the goal of maximizing received rewards. For example, an RL algorithm might control the moves (actions) of a character (the agent) in a video game (the environment), aiming to maximize the score (the reward). In robotics, an RL algorithm might control the movements (actions) of a robot (the agent) in the world (the environment) to perform a task (earning a reward). In finance, an RL algorithm might control a virtual trader (the agent) who buys or sells assets (the actions) on a trading platform (the environment) to maximize profit (the reward).

## 19.1 Markov decision processes, returns, and policies

### 19.1.2 Markov reward process

> ![19.2](/contents/understanding-deep-learning/19.2.png)
>
> Figure 19.2 Markov reward process. This associates a distribution P r(rt+1 |st ) of rewards rt+1 with each state st. a) Here, the rewards are deterministic; the penguin will receive a reward of +1 if it lands on a fish and 0 otherwise. The trajectory τ now consists of a sequence s1,r2,s2,r3,s3,r4 ... of alternating states and rewards, terminating after eight steps. The return Gt of the sequence is the sum of discounted future rewards, here with discount factor γ = 0.9. b-c) As the penguin proceeds along the trajectory and gets closer to reaching the rewards, the return increases.

> ![19.3](/contents/understanding-deep-learning/19.3.png)
>
> Figure 19.3 Markov decision process. a) The agent (penguin) can perform one of a set of actions in each state. The action influences both the probability of moving to the successor state and the probability of receiving rewards. b) Here, the four actions correspond to moving up, right, down, and left. c) For any state (here, state 6), the action changes the probability of moving to the next state. The penguin moves in the intended direction with 50% probability, but the ice is slippery, so it may slide to one of the other adjacent positions with equal probability. Accordingly, in panel (a), the action taken (gray arrows) doesn’t always line up with the trajectory (orange line). Here, the action does not affect the reward, so Pr(rt+1|st,at) = Pr(rt+1|st). The trajectory τ from an MDP consists of a sequence s1, a1, r2, s2, a2, r3, s3, a3, r4 . . . of alternating states st, actions at, and rewards, rt+1. Note that here the penguin receives the reward when it leaves a state with a fish (i.e., the reward is received for passing through the fish square, regardless of whether the penguin arrived there intentionally or not).

## 19.3 Tabular reinforcement learning

> ![19.10](/contents/understanding-deep-learning/19.10.png)
>
> Figure 19.10 Dynamic programming. a) The state values are initialized to zero, and the policy (arrows) is chosen randomly. b) The state values are updated to be consistent with their neighbors (equation 19.11, shown after two iterations). The policy is updated to move the agent to states with the highest value (equation 19.12). c) After several iterations, the algorithm converges to the optimal policy, in which the penguin tries to avoid the holes and reach the fish.

# Chapter 20 Why does deep learning work?

## 20.4 Factors that determine generalization

### 20.4.6 Leaving the data manifold

> ![20.14](/contents/understanding-deep-learning/20.14.png)
>
> Figure 20.14 Adversarial examples. In each case, the left image is correctly classified by AlexNet. By considering the gradients of the network output with respect to the input, it’s possible to find a small perturbation (center, magnified by 10 for visibility) that, when added to the original image (right), causes the network to misclassify it as an ostrich. This is despite the fact that the original and perturbed images are almost indistinguishable to humans. Adapted from Szegedy et al. (2014).

## 20.5 Do we need so many parameters?

### 20.5.1 Pruning

> ![20.15](/contents/understanding-deep-learning/20.15.png)
>
> Figure 20.15 Pruning neural networks. The goal is to remove as many weights as possible without decreasing performance. This is often done just based on the magnitude of the weights. Typically, the network is fine-tuned after pruning. a) Example fully connected network. b) After pruning.

# Chapter 21 Deep learning and ethics

## 21.3 Other social, ethical, and professional issues

### 21.3.3 Environmental impact

> Strubell et al. (2019, 2020) estimate that training a transformer model with 213 million parameters emitted around 284 tonnes of CO2.

> As a baseline, it is estimated that the average human is responsible for around 5 tonnes of CO2 per year, with individuals from major oil-producing countries responsible for three times this amount. See https://ourworldindata.org/co2-emissions.

# Appendix C Probability

## C.1 Random variables and probability distributions

### C.1.1 Joint probability

> ![C.1](/contents/understanding-deep-learning/C.1.png)
>
> Figure C.1 Joint and marginal distributions. a) The joint distribution Pr(x,y) captures the propensity of variables x and y to take different combinations of values. Here, the probability density is represented by the color map, so brighter positions are more probable. For example, the combination x=6,y=6 is much less likely to be observed than the combination x = 5, y = 0. b) The marginal distribution Pr(x) of variable x can be recovered by integrating over y. c) The marginal distribution P r(y) of variable y can be recovered by integrating over x.

### C.1.3 Conditional probability and likelihood

> The conditional probability P r(x|y) is the probability of variable x taking a certain value, assuming we know the value of y. The vertical line is read as the English word “given,” so Pr(x|y) is the probability of x given y.

> ![C.2](/contents/understanding-deep-learning/C.2.png)
>
> Figure C.2 Conditional distributions. a) Joint distribution P r(x, y) of variables x and y. b) The conditional probability Pr(x|y = 3.0) of variable x, given that y takes the value 3.0, is found by taking the horizontal “slice” P r(x, y = 3.0) of the joint probability (top cyan line in panel a), and dividing this by the total area Pr(y = 3.0) in that slice so that it forms a valid probability distribution that integrates to one. c) The joint probability Pr(x,y=−1.0) is found similarly using the slice at y=−1.0.

### C.1.4 Bayes’ rule

> ![C.3](/contents/understanding-deep-learning/C.3.png)
>
> Figure C.3 Independence. a) When two variables x and y are independent, the joint distribution factors into the product of marginal distributions, so P r(x, y) = P r(x)P r(y). Independence implies that knowing the value of one variable tells us nothing about the other. b–c) Accordingly, all of the conditional distributions P r(x|y = •) are the same and are equal to the marginal distribution P r(x).

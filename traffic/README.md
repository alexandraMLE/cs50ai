NEURAL NETWORK — cs50ai traffic project 5

During the course of this project, I experimented with varying a number of parameters: 
                                number of convolutional layers 
                                number of pooling layers
                                pool sizes for each pooling layer 
                                number of hidden layers 
                                hidden layer sizes 
                                dropout value

I initially started with baseline conditions, as per shown in the lectures, to classify MNIST images: 
                • 1 convolutional layer learning 32 filters with a 3x3 kernel 
                • 1 pooling layer with size 2x2 
                • 1 hidden layer with 128 neurons 
                • 0.5 dropout

With modification, from above, of the parameters one by one to observe effect on accuracy, 
I found adding more convolutional layers was most beneficial.
I determined the parameters set: 
                • convolutional layer learning 64 filters with a 4x4 kernel 
                • convolutional layer learning 64 filters with a 3x3 kernel 
                • convolutional layer learning 64 filters with a 3x3 kernel
                • pooling layer with size 2x2 
                • hidden layer with 128 neurons 
                • hidden layer with 64 neurons 
                • 0.5 dropout

resulted in a testing accuracy of 97.6% (averaging 5 independent runs) with the highest testing 
accuracy of 98.3%. This was the highest accuracy I found under my own influence; 
common ConvNet architectures (found online after research) resulted in varying testing accuracies.

If you have any suggestions/comments on different parameters or architectures to try, 
or any suggestions to improve the efficiency of my code — contact me — a.lee.epstein@gmail.com

GitHub:   alexandraMLE
edX:        alexandraMLE

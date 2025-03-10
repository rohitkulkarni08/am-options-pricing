# am-options-pricing
Masters Project - Options Pricing Model

## Abstract

Goal:
Part-a Analysis:
1. See how Binomal Tree model works for options pricing for American options
2. Run tests like convergence tests/Least Squares Monte Carlo to evaluate the accuracy of the model

Part-b Better model (Neural Networks):
1. Use additional metrics which are not used in binomial tree based option pricing model like Moneyless, RSI, MACD, additional volatilities, greeks etc to build a neural network based model
2. Using daily stock data for each ticker (for a bunch of stocks), compute the option price using binomial tree method and set that as a target variable and train a neural network on that
3. Optimize Neural Network

Part-c Product:
1. Since my project/product is mainly targeted by someone who is not that experienced in option pricing/finance, I want to build a NLQ based model which will take a queried input and give a bunch of insights (which will be based on Neural network output mainly but will also show other models for comparison)
2. Insights:
 i) Option price based on the data obtained from the query
ii) Add like a scale of sorts where I can alter/modify constraints to see how the price will differ based on different conditions (Ex. interest rates, volatility etc.)

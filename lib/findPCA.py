#!/Users/vk/miniconda3/bin/python

import pandas as pd
from sklearn.decomposition import PCA

class PrincipalComponentAnalysis():

    def __init__(self, data, varPercent):
        data = self.data
        varPercent = self.varPercent
    
    
    def findPCA(data,varPercent):
        
        try:
            
            data = data.dropna()
            
            features = ['marketClose','notional','momentum_rsi','momentum_stoch','trend_aroon_ind']

            # Separating out the features
            x = data.loc[:, features].values

            # Separating out the target
            y = data.loc[:,['target']].values

            pca = PCA(n_components=0.95)
            pc = pca.fit_transform(x)

            pc_df = pd.DataFrame(data = pc)
            pc_df['target'] = y
            
            pc_df = pc_df.round(3)

            return (pc_df)
        except:
            print ("Error in PrincipalComponentAnalysis class - findPCA method: Please check")
        

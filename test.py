import pandas as pd

df = pd.read_csv('sitemap_layers copy.csv')
layers = 3
for i in range(1, layers+1):
    cols = [str(i_) for i_ in range(i)]
    print(cols)
    nodes = df[cols].drop_duplicates().values
    print(nodes)
    for j, k in enumerate(nodes):
        mask = True
        for j_, ki in enumerate(k):
                mask &= df[str(j_)] == ki
                # print(mask)
        print("Tried to use key" + str(i-1))
        data = df[mask].groupby([str(i-1)])['counts'].sum().reset_index().sort_values(['counts'], ascending=False)
        print(data)
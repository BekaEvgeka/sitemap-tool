
from __future__ import print_function
# Set global variables

categorization_depth = 4


# Import external library dependencies

import pandas as pd
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--depth', type=int, default=categorization_depth,
                    help='Number of layers deep to categorize')
args = parser.parse_args()


# Update variables with arguments if included

categorization_depth = args.depth



# Main script functions


def peel_layers(urls, layers=3):

    # Store results in a dataframe
    sitemap_layers = pd.DataFrame()

    # Get base levels
    bases = pd.Series([url.split('//')[-1].split('/')[0] for url in urls])
    sitemap_layers[0] = bases

    # Get specified number of layers
    for layer in range(1, layers+1):

        page_layer = []
        for url, base in zip(urls, bases):
            try:
                page_layer.append(url.split(base)[-1].split('/')[layer])
            except:
                # There is nothing that deep!
                page_layer.append('')

        sitemap_layers[layer] = page_layer

    # Count and drop duplicate rows + sort
    sitemap_layers = sitemap_layers.groupby(list(range(0, layers+1)))[0].count()\
                     .rename('counts').reset_index()\
                     .sort_values('counts', ascending=False)\
                     .sort_values(list(range(0, layers)), ascending=True)\
                     .reset_index(drop=True)

    # Convert column names to string types and export
    sitemap_layers.columns = [str(col) for col in sitemap_layers.columns]
    sitemap_layers.to_csv('sitemap_layers.csv', index=False)

    # Return the dataframe
    return sitemap_layers


def main():

    sitemap_urls = open('sitemap_urls.dat', 'r').read().splitlines()
    print('Loaded {:,} URLs'.format(len(sitemap_urls)))

    print('Categorizing up to a depth of %d' % categorization_depth)
    sitemap_layers = peel_layers(urls=sitemap_urls,
                                 layers=categorization_depth)
    print('Printed {:,} rows of data to sitemap_layers.csv'.format(len(sitemap_layers)))


if __name__ == '__main__':
    main()

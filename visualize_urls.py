
from __future__ import print_function

graph_depth = 3  # Number of layers deep to plot categorization
limit = 50       # Maximum number of nodes for a branch
title = ''       # Graph title
style = 'light'  # Graph style, can be "light" or "dark"
size = '8,5'     # Size of rendered graph
output_format = 'pdf'   # Format of rendered image - pdf,png,tiff
skip = ''        # List of branches to restrict from expanding
search = ''

# Import external library dependencies

import pandas as pd
import graphviz
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--depth', type=int, default=graph_depth,
                    help='Number of layers deep to plot categorization')
parser.add_argument('--limit', type=int, default=limit,
                    help='Maximum number of nodes for a branch')
parser.add_argument('--title', type=str, default=title,
                    help='Graph title')
parser.add_argument('--style', type=str, default=style,
                    help='Graph style, can be "light" or "dark"')
parser.add_argument('--size', type=str, default=size,
                    help='Size of rendered graph')
parser.add_argument('--output-format', type=str, default=output_format,
                    help='Format of the graph you want to save. Allowed formats are jpg, png, pdf or tif')
parser.add_argument('--skip', type=str, default=skip,
        help="List of branches that you do not want to expand. Comma separated: e.g. --skip 'news,events,datasets'")
parser.add_argument('--search', type=str, default='no_search')
args = parser.parse_args()


# Update variables with arguments if included

graph_depth = args.depth
limit = args.limit
title = args.title
style = args.style
size = args.size
output_format = args.output_format
skip = args.skip.split(',')
search = args.search

# Main script functions

def make_sitemap_graph(df, layers=graph_depth, limit=limit, size=size, output_format=output_format, skip=skip):
    
    # Check to make sure we are not trying to plot too many layers
    if layers > len(df) - 1:
        layers = len(df)-1
        print('There are only %d layers available to plot, setting layers=%d'
              % (layers, layers))


    # Initialize graph
    f = graphviz.Digraph('sitemap', filename='sitemap_graph_%d_layer' % layers, format='%s' % output_format)
    f.body.extend(['rankdir="LR"', 'size="%s"' % size])


    def add_branch(f, names, vals, limit, connect_to=''):

        # Get the currently existing node names
        node_names = [item.split('"')[1] for item in f.body if 'label' in item]

        # Only add a new branch it it will connect to a previously created node
        if connect_to:
            if connect_to in node_names:
                for name, val in list(zip(names, vals))[:limit]:
                    if name in search:
                        f.attr('node', shape='rectangle', fillcolor='red')
                        f.node(name='%s-%s' % (connect_to, name), label=name)
                        f.edge(connect_to, '%s-%s' % (connect_to, name), label='{:,}'.format(val))
                        f.graph_attr.update()
                    else:
                        f.attr('node', shape='oval', fillcolor='white')
                        f.node(name='%s-%s' % (connect_to, name), label=name)
                        f.edge(connect_to, '%s-%s' % (connect_to, name), label='{:,}'.format(val))
                        f.graph_attr.update()
                      
    f.attr('node', shape='rectangle') # Plot nodes as rectangles

    # Add the first layer of nodes
    for name, counts in df.groupby(['0'])['counts'].sum().reset_index()\
                          .sort_values(['counts'], ascending=False).values:
        f.node(name=name, label='{} ({:,})'.format(name, counts))
    if layers == 0:
        return f

    f.attr('node', shape='oval') # Plot nodes as ovals
    f.graph_attr.update()

    # Loop over each layer adding nodes and edges to prior nodes
    for i in range(1, layers+1):
        cols = [str(i_) for i_ in range(i)]
        nodes = df[cols].drop_duplicates().values
        for j, k in enumerate(nodes):

            # Compute the mask to select correct data
            mask = True
            for j_, ki in enumerate(k):
                mask &= df[str(j_)] == ki

            # Select the data then count branch size, sort, and truncate
            data = df[mask].groupby([str(i)])['counts'].sum()\
                    .reset_index().sort_values(['counts'], ascending=False)

            # Add to the graph unless specified that we do not want to expand k-1
            if (not skip) or (k[-1] not in skip):
                add_branch(f,
                       names=data[str(i)].values,
                       vals=data['counts'].values,
                       limit=limit,
                       connect_to='-'.join(['%s']*i) % tuple(k))

            print(('Built graph up to node %d / %d in layer %d' % (j, len(nodes), i))\
                    .ljust(50), end='\r')

    return f


def apply_style(f, style, title=''):
    
    dark_style = {
        'graph': {
            'label': title,
            'bgcolor': '#3a3a3a',
            'fontname': 'Helvetica',
            'fontsize': '18',
            'fontcolor': 'white',
        },
        'nodes': {
            'style': 'filled',
            'color': 'white',
            'fillcolor': 'black',
            'fontname': 'Helvetica',
            'fontsize': '14',
            'fontcolor': 'white',
        },
        'edges': {
            'color': 'white',
            'arrowhead': 'open',
            'fontname': 'Helvetica',
            'fontsize': '12',
            'fontcolor': 'white',
        }
    }

    light_style = {
        'graph': {
            'label': title,
            'fontname': 'Helvetica',
            'fontsize': '18',
            'fontcolor': 'black',
        },
        'nodes': {
            'style': 'filled',
            'color': 'black',
            'fillcolor': '#dbdddd',
            'fontname': 'Helvetica',
            'fontsize': '14',
            'fontcolor': 'black',
        },
        'edges': {
            'color': 'black',
            'arrowhead': 'open',
            'fontname': 'Helvetica',
            'fontsize': '12',
            'fontcolor': 'black',
        }
    }

    if style == 'light':
        apply_style = light_style

    elif style == 'dark':
        apply_style = dark_style

    f.graph_attr = apply_style['graph']
    f.node_attr = apply_style['nodes']
    f.edge_attr = apply_style['edges']

    return f

def main():

    # Read in categorized data
    sitemap_layers = pd.read_csv('sitemap_layers.csv', dtype=str)
    # Convert numerical column to integer
    sitemap_layers.counts = sitemap_layers.counts.apply(int)
    print('Loaded {:,} rows of categorized data from sitemap_layers.csv'\
            .format(len(sitemap_layers)))

    print('Building %d layer deep sitemap graph' % graph_depth)
    f = make_sitemap_graph(sitemap_layers, layers=graph_depth,
                            limit=limit, size=size, output_format=output_format, skip=skip)
    f = apply_style(f, style='light', title=title)

    f.render(cleanup=True)

    print('Exported graph to sitemap_graph_%d_layer.%s' % (graph_depth, output_format))

if __name__ == '__main__':
    main()

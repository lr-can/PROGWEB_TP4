import flask
import sqlite3
import sql_requests
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import io


app = flask.Flask(__name__)



@app.route('/')
def index():
    """
    Render the application's index page.
    Fetches data via sql_requests.fetch_for_index() and renders the 'index.html'
    template with the retrieved rows available in the template context under the
    'name' "rows".
    No parameters.
    Returns:
        A Flask response object (the rendered template) as returned by
        flask.render_template('index.html', rows=rows).
    Raises:
        Any exceptions raised by sql_requests.fetch_for_index() (for example
        database errors) or by flask.render_template() (for example template not
        found) will propagate to the caller.
    Side effects:
        Performs a database query to obtain the rows used to populate the page.    
    """

    rows = sql_requests.fetch_for_index()
    return flask.render_template('index.html', rows=rows)



@app.route('/parts/<part>/genes')
def genes_by_part(part):
    """
    Render a page showing genes associated with a specific part.
    Fetches data via sql_requests.fetch_genes_by_part(part) and renders the
    'parts_genes.html' template with the retrieved rows available in the template
    context under the name "rows", and the part under the name "part".
    Parameters:
        part (str): The part identifier used to filter genes.
    Returns:
        A Flask response object (the rendered template) as returned by
        flask.render_template('parts_genes.html', part=part, rows=rows).
    Raises:
        Any exceptions raised by sql_requests.fetch_genes_by_part(part) (for
        example database errors) or by flask.render_template() (for example
        template not found) will propagate to the caller.
    Side effects:
        Performs a database query to obtain the rows used to populate the page. 
    """

    rows = sql_requests.fetch_genes_by_part(part)
    return flask.render_template('parts_genes.html', part=part, rows=rows)



@app.route('/genes/<gene_id>')
def gene_by_id(gene_id):
    """
    Render a page showing detailed information about a specific gene.
    Fetches data via sql_requests.fetch_gene_by_id(gene_id) and renders the
    'gene_info.html' template with the retrieved rows available in the template
    context under the names "row", "transcrits", and "parts".
    Parameters:
        gene_id (str): The gene identifier used to fetch detailed information.
    Returns:
        A Flask response object (the rendered template) as returned by
        flask.render_template('gene_info.html', row=row, transcrits=row2, parts=row3).
    Raises:
        Any exceptions raised by sql_requests.fetch_gene_by_id(gene_id) (for
        example database errors) or by flask.render_template() (for example
        template not found) will propagate to the caller.
    Side effects:
        Performs a database query to obtain the rows used to populate the page. 
    """

    row, row2, row3 = sql_requests.fetch_gene_by_id(gene_id)
    return flask.render_template('gene_info.html', row=row, transcrits=row2, parts=row3)



@app.route('/genes/<gene_id>/edit', methods=['GET', 'POST'])
def edit_gene(gene_id):
    """
    Handle editing of a specific gene's information.
    For GET requests, fetches data via sql_requests.fetch_gene_by_id(gene_id)
    and renders the 'edit_gene.html' template with the retrieved row available
    in the template context under the name "row".
    For POST requests, updates the gene information using
    sql_requests.update_gene(gene_id, form_data) where form_data is obtained
    from the submitted form, and then redirects to the gene's detail page.
    Parameters:
        gene_id (str): The gene identifier used to fetch and update information.
    Returns:
        For GET requests: A Flask response object (the rendered template) as
        returned by flask.render_template('edit_gene.html', row=row).
        For POST requests: A Flask redirect response to the gene's detail page
        as returned by flask.redirect(f'/genes/{gene_id}').
    Raises:
        Any exceptions raised by sql_requests.fetch_gene_by_id(gene_id) or
        sql_requests.update_gene(gene_id, form_data) (for example database
        errors) or by flask.render_template() (for example template not found)
        will propagate to the caller.
    Side effects:
        Performs a database query to obtain the row used to populate the edit
        page for GET requests, and updates the database with new information for
        POST requests.
    """


    if flask.request.method == 'POST':
        form_data = flask.request.form
        sql_requests.update_gene(gene_id, form_data)
        return flask.redirect(f'/genes/{gene_id}')
    else:
        row, row2, row3 = sql_requests.fetch_gene_by_id(gene_id)
        return flask.render_template('edit_gene.html', row=row)



@app.route('/transcripts/<transcript_id>')
def transcript_by_id(transcript_id):
    """
    Render a page showing detailed information about a specific transcript.
    Fetches data via sql_requests.fetch_transcript_by_id(transcript_id) and
    renders the 'transcript_info.html' template with the retrieved rows
    available in the template context under the names "row" and "parts".
    Parameters:
        transcript_id (str): The transcript identifier used to fetch detailed information.
    Returns:
        A Flask response object (the rendered template) as returned by
        flask.render_template('transcript_info.html', row=row1, parts=row2).
    Raises:
        Any exceptions raised by sql_requests.fetch_transcript_by_id(transcript_id) (for
        example database errors) or by flask.render_template() (for example
        template not found) will propagate to the caller.
    Side effects:
        Performs a database query to obtain the rows used to populate the page. 
    """

    row1, row2 = sql_requests.fetch_transcript_by_id(transcript_id)
    return flask.render_template('transcript_info.html', row=row1, parts=row2)




@app.route('/genes/<gene_id>/parts.png')
# def gene_parts_plot(gene_id):
#     data_for_png = sql_requests.plot_gene_parts(gene_id)
#     fig, ax = plt.subplots()
#     keys = list(data_for_png.keys())
#     values = list(data_for_png.values())
#     ax.hist(keys, weights=values, bins=len(keys), align='mid')
#     ax.set_xlabel('Parts')
#     ax.set_ylabel('Counts')
#     ax.set_title(f'Gene {gene_id} parts distribution')
#     plt.xticks(rotation=90)
#     plt.tight_layout()
#     png_path = f'static/{gene_id}_parts.png'
#     plt.savefig(png_path)
#     plt.close(fig)
#     return flask.send_file(png_path, mimetype='image/png')
def gene_parts_plot(gene_id):
    """
    Generate and return a PNG plot showing the distribution of parts for a specific gene.
    Fetches data via sql_requests.plot_gene_parts(gene_id), creates a histogram
    using Matplotlib, and returns the plot as a PNG image.
    Parameters:
        gene_id (str): The gene identifier used to fetch parts distribution data.
    Returns:
        A Flask response object containing the PNG image of the plot, with
        mimetype 'image/png'.
    Raises:
        Any exceptions raised by sql_requests.plot_gene_parts(gene_id) (for
        example database errors) or by Matplotlib functions (for example
        plotting errors) will propagate to the caller.
    Side effects:
        Performs a database query to obtain the data used to generate the plot.
    """

    data_for_png = sql_requests.plot_gene_parts(gene_id)
    fig, ax = plt.subplots()
    keys = list(data_for_png.keys())
    values = list(data_for_png.values())
    if keys:
        ax.hist(keys, weights=values, bins=len(keys), align='mid')
        ax.set_xlabel('Parts')
        ax.set_ylabel('Counts')
        ax.set_title(f'Gene {gene_id} parts distribution')
        plt.xticks(rotation=90)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return flask.send_file(buf, mimetype='image/png') # All parts have the same count



@app.route('/genes/<gene_id>/transcripts.svg')
def gene_transcripts_svg(gene_id):
    """
    Generate and return an SVG representation of the transcripts for a specific gene.
    Fetches data via sql_requests.fetch_gene_by_id(gene_id), processes the
    transcript coordinates, and renders an SVG using a Jinja2 template.
    Parameters:
        gene_id (str): The gene identifier used to fetch transcript data.
    Returns:
        A Flask response object containing the SVG image, with mimetype
        'image/svg+xml'.
    Raises:
        Any exceptions raised by sql_requests.fetch_gene_by_id(gene_id) (for
        example database errors) or by flask.render_template() (for example
        template not found) will propagate to the caller.
    Side effects:
        Performs a database query to obtain the transcript data used to generate
        the SVG.
    """

    _, row2, _ = sql_requests.fetch_gene_by_id(gene_id) # we only need transcripts (row2)

    coordinates = []
    for i, tr in enumerate(row2 or []):
        coordinates.append({
            "id_tr": tr["Ensembl_Transcript_ID"],
            "start": int(tr["Transcript_Start"]),
            "end":   int(tr["Transcript_End"]),
            "y":     30*i + 20 
        }) 


    if not coordinates: # if there are no transcripts
        svg = flask.render_template('gene_transcripts.svg.j2',
                              width=800, height=50, coordinates=[])
        return flask.Response(svg, mimetype="image/svg+xml")


    # Compute scaling factors and positions to fit within 800px width
    width_px  = 800
    margin_px = 20
    inner_w   = width_px - 2*margin_px
    min_start = min(c["start"] for c in coordinates)
    max_end   = max(c["end"]   for c in coordinates)
    span      = max(1, max_end - min_start)
    scale     = inner_w / span

    # Update coordinates with scaled positions and widths
    for c in coordinates:
        c["x"] = margin_px + int((c["start"] - min_start) * scale)
        c["w"] = max(1, int((c["end"] - c["start"]) * scale))  # min 1 px

    # Compute SVG height
    height = 30 * len(coordinates) + 50

    # Define colors (pour aller plus loin)
    colors = ['#dde5ff', '#88fdaa', '#ffded9', '#ffdddd']
    colors_text = ['#0063cb', '#18753c', '#b34000', '#ce0500']

    svg = flask.render_template('gene_transcripts.svg.j2',
                          width=width_px, height=height, coordinates=coordinates, colors=colors, colors_text=colors_text)
    return flask.Response(svg, mimetype="image/svg+xml")
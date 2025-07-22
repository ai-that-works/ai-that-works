

def analyze_pages_with_transactions(pages: BamlImage[]):
    ref_page = pages[0]
    headers_footers: (y1, y2)[] = []
    for other in pages[1:]:
        header = compare_pages(ref_page, other, 0, 1, "./data/same")
        headers_footers.append(header)
    
    # find most common header/footer
    most_common_header: (y1, y2)[2] = ask_llm(headers_footers, pages)
    
    txns: Txn[] = []
    previous_page: BamlImage | None = None
    for i, page in enumerate(pages):
        new_image = mask_image(page, header=most_common_header[0], footer=most_common_header[1])
        curr_ctx = [new_image]
        if i > 0:
            continued_from_previous_page = compare_pages(new_image, previous_page)
            if continued_from_previous_page:
                # crop top 75% of previous page
                prev_page_cropped = previous_page.crop((0, 0, previous_page.width, int(previous_page.height * 0.75)))
                curr_ctx.append(prev_page_cropped)
        
        # check for dups:
        new_txns = extract_transactions(curr_ctx)
        txns = get_tnxs_without_dups(txns, new_txns)
        previous_page = new_image
    
    return txns


from . import sec_edgar, techcrunch, vcru

REGISTRY = {
    "sec_edgar": sec_edgar.fetch,
    "techcrunch": techcrunch.fetch,
    "vcru": vcru.fetch,
}

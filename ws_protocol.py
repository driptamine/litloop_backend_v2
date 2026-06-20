# In /home/driptamine/litloop_backend_v2/env/lib/python3.10/site-packages/daphne/ws_protocol.py, find the onClose method (around line 161) and change it from:
def onClose(self, wasClean, code, reason):
    """
    Called when Twisted closes the socket.
    """
    if not hasattr(self, "server") or self.server is None:
        logger.debug("WebSocket closed without server (Hixie76 probe)")
        return
    self.server.protocol_disconnected(self)
    logger.debug("WebSocket closed for %s", self.client_addr)
    if not self.muted and hasattr(self, "application_queue"):
        self.application_queue.put_nowait(
            {"type": "websocket.disconnect", "code": code}
        )
    self.server.log_action(
        "websocket",
        "disconnected",
        {
            "path": self.request.path,
            "client": (
                "%s:%s" % tuple(self.client_addr) if self.client_addr else None
            ),
        },
    )
# Then sudo systemctl restart daphne.

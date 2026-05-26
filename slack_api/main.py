from message import *
from slack import *

# A dictionary grouping cover letter tones by company culture type
cover_letter_tones = {
    "corporate": [
        "professional",
        "authoritative",
        "formal",
        "polished",
        "concise",
        "direct",
    ],
    "modern": [
        "conversational",
        "professional yet approachable",
        "confident",
        "enthusiastic",
        "collaborative",
    ],
    "creative": ["personality-forward", "bold", "witty", "engaging", "story-driven"],
    "mission_driven": [
        "values-aligned",
        "passionate",
        "inspiring",
        "empathetic",
        "community-focused",
    ],
}


def main():

    message_blocks = create_blocks(
        job_title="Senior Frontend Developer",
        proposal="Hi team,\n\nI'm excited to apply for this role...\n\n— John Doe",
        budget="Hourly",
        client_rating="4.22",
        location="San Diego, United States",
        hire_rate="66%",
        avg_rate="$22.90/hr, 231 hrs",
        apply_url="https://www.google.com",
    )
    send_via_bot(channel="#social", blocks=message_blocks)


if __name__ == "__main__":
    main()
    from fastapi import FastAPI

    from users.routes import router as users_router
    from products.routes import router as products_router
    from orders.routes import router as orders_router

    app = FastAPI()

    app.include_router(users_router)
    app.include_router(products_router)
    app.include_router(orders_router)

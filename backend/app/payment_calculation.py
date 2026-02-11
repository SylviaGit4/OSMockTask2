'''This module contains the calculation for the total cost of a zoo visit & hotel.
'''

def calculate_cost(child_tickets, adult_tickets, visit_time, educational_visit, room_price, hotel_time):
    child_ticket_value = 10
    adult_ticket_value = 20
    educational_visit_discount = 0.9 # 10% discount for educational visits

    total_ticket_cost = (child_tickets * child_ticket_value) + (adult_tickets * adult_ticket_value)
    total_visit_cost = visit_time * total_ticket_cost

    if educational_visit:
        total_visit_cost *= educational_visit_discount

    total_hotel_cost = room_price * hotel_time

    total_cost = total_visit_cost + total_hotel_cost

    return total_cost

// FullCalendar integration for GlobeTrotter

document.addEventListener('DOMContentLoaded', function() {
    // Calendar initialization is handled in the template
    // This file can be extended with custom calendar functionality
});

// Custom event rendering
function renderEventContent(eventInfo) {
    return {
        html: `
            <div class="fc-event-title">${eventInfo.event.title}</div>
            ${eventInfo.event.extendedProps.city ? `<div class="fc-event-city">${eventInfo.event.extendedProps.city}</div>` : ''}
        `
    };
}

// Event click handler
function handleEventClick(info) {
    const props = info.event.extendedProps;
    const content = `
        <div>
            <h6>${info.event.title}</h6>
            ${props.activity_type ? `<p><strong>Type:</strong> ${props.activity_type}</p>` : ''}
            ${props.duration ? `<p><strong>Duration:</strong> ${props.duration} hours</p>` : ''}
            ${props.cost ? `<p><strong>Cost:</strong> ₹${props.cost.toFixed(2)}</p>` : ''}
            ${props.city ? `<p><strong>City:</strong> ${props.city}</p>` : ''}
            ${props.notes ? `<p><strong>Notes:</strong> ${props.notes}</p>` : ''}
        </div>
    `;
    
    // You can customize this to show a modal or tooltip
    alert(content);
}


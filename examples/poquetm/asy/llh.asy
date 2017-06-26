
settings.outformat = "pdf";
unitsize(1cm);
from job access *;
from gantt_examples access generate_energy_jobs;

Job[] generate_llh_jobs()
{
    Job j1, j2, j3, j4;

    j1.id = "1";
    j1.number_of_requested_resources = 1;
    j1.processing_time = 2;
    j1.requested_time = 3;

    j2.id = "2";
    j2.number_of_requested_resources = 3;
    j2.processing_time = 1;
    j2.requested_time = 2;

    j3.id = "3";
    j3.number_of_requested_resources = 2;
    j3.processing_time = 2;
    j3.requested_time = 3;

    j4.id = "4";
    j4.number_of_requested_resources = 1;
    j4.processing_time = 1;
    j4.requested_time = 1;

    int s = 255, w=225;
    j1.fill_color = rgb(w/1.2,s,w/1.2);
    j2.fill_color = rgb(w,s,w);
    j3.fill_color = rgb(w,w,s);
    j4.fill_color = rgb(s,w,w);

    Job[] jobs = {j1, j2, j3, j4};
    return jobs;
}

void figures_llh()
{
    // Let's define the jobs
    Job jobs[] = generate_llh_jobs();
    Job energy_jobs[] = generate_energy_jobs();
    Job j1, j2, j3, j4, json, jsoff, joff;

    j1 = jobs[0];
    j2 = jobs[1];
    j3 = jobs[2];
    j4 = jobs[3];
    json = energy_jobs[0];
    jsoff = energy_jobs[1];
    joff = energy_jobs[2];

    joff.processing_time = 3;

    // Figure 1: previsional schedule
    // Let's draw the frame
    draw_frame(0,3, 0,5, draw_time_axe_values=false);
    real dash_width = 1/8;
    label("$t$", (0,0-dash_width), align=down);
    label("$t\!+\!1$", (1,0-dash_width), align=down);
    label("$t\!+\!2$", (2,0-dash_width), align=down);
    label("$t\!+\!3$", (3,0-dash_width), align=down);

    // Let's draw the jobs
    draw_job_on_position(j1, (0,0), draw_requested_time=true);
    draw_job_on_position(j2, (0,1), draw_requested_time=true);
    draw_job_on_position(joff, (0,4), draw_requested_time=false);

    // Draw infinite OFF
    draw((3,4) -- (4,4), dotted);
    draw((3,5) -- (4,5), dotted);
    label("$\rightarrow \infty$", (3.5, 4.5));

    label("Queue load = 7", (6.5,4.5));
    draw_job_on_position(j3, (5,2), draw_requested_time=true);
    draw_job_on_position(j4, (5,1), draw_requested_time=true);

    shipout("llh_previsional_schedule");
    erase();

    // Figure 2: llh
    // Let's draw the frame
    draw_frame(0,4, 0,5, draw_time_axe_values=false);
    real dash_width = 1/8;
    label("$t$", (0,0-dash_width), align=down);
    label("$t\!+\!1$", (1,0-dash_width), align=down);
    label("$t\!+\!2$", (2,0-dash_width), align=down);
    label("$t\!+\!3$", (3,0-dash_width), align=down);
    label("$t\!+\!4$", (4,0-dash_width), align=down);

    // Let's draw the jobs
    draw_job_on_position(j1, (0,0), draw_requested_time=true);
    draw_job_on_position(j2, (0,1), draw_requested_time=true);
    joff.processing_time=5;
    draw_job_on_position(joff, (0,4), draw_requested_time=false);

    // Draw infinite OFF
    draw((5,4) -- (6,4), dotted);
    draw((5,5) -- (6,5), dotted);
    label("$\rightarrow \infty$", (5.5, 4.5));

    // Let's draw the LLH area
    real j3_x = 3 + 3.0/4.0;
    path borders3 = (3,0) -- (j3_x,0) -- (j3_x,4) -- (2,4) -- (2,1) -- (3,1) -- cycle;
    filldraw(borders3, j3.fill_color);

    real j4_x = j3_x + 1.0/4.0;
    path borders4 = (j3_x,0) -- (j4_x,0) -- (j4_x,4) -- (j3_x,4) -- cycle;
    filldraw(borders4, j4.fill_color);

    // Let's draw the LLH
    draw((0,5.25) -- (4,5.25), Arrow);
    draw((0,5.25) -- (4,5.25) -- cycle, Arrow);
    label("$llh=4$", (2,5.25), align=up);

    // Invisible point to make sure the two figures have the same size
    draw(circle(8,0), opacity(0));

    shipout("llh_visualised");
}

figures_llh();
erase();
